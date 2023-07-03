package main

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strings"

	"github.com/pdfcpu/pdfcpu/pkg/api"
	"github.com/pdfcpu/pdfcpu/pkg/pdfcpu/model"
	"github.com/pkg/errors"
)

// App struct
type App struct {
	ctx context.Context
}

// NewApp creates a new App application struct
func NewApp() *App {
	return &App{}
}

// startup is called when the app starts. The context is saved
// so we can call the runtime methods
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
}

// My app part
type MyConfig struct {
	PdfPath    string `json:"pdf_path"`
	OcrPath    string `json:"ocr_path"`
	PandocPath string `json:"pandoc_path"`
}

func (a *App) SaveConfig(pdfPath string, ocrPath string, pandocPath string) error {
	var config MyConfig
	config.PdfPath = pdfPath
	config.OcrPath = ocrPath
	config.PandocPath = pandocPath
	jsonData, err := json.Marshal(config)
	if err != nil {
		fmt.Println(err)
		return err
	}
	filename := "config.json"
	err = os.WriteFile(filename, jsonData, 0644)
	if err != nil {
		fmt.Println("Error:", err)
		return err
	}
	return nil
}

func (a *App) LoadConfig() (MyConfig, error) {
	configPath := "config.json"
	var config MyConfig
	if _, err := os.Stat(configPath); os.IsNotExist(err) {
		path, err := os.Executable()
		if err != nil {
			fmt.Println("Error:", err)
			return config, err
		}
		path = filepath.Join(filepath.Dir(path), "pdf.exe")
		err = a.SaveConfig(path, "", "")
		if err != nil {
			return config, err
		}
	}
	data, err := os.ReadFile(configPath)
	if err != nil {
		return config, err
	}
	err = json.Unmarshal(data, &config)
	if err != nil {
		return config, err
	}
	return config, nil
}

func CheckCmdError(cmd *exec.Cmd) error {
	stderr, err := cmd.StderrPipe()
	if err != nil {
		log.Printf("Error: %v\n", err)
		return err
	}
	if err := cmd.Start(); err != nil {
		log.Printf("Error: %v\n", err)
		return err
	}
	scanner := bufio.NewScanner(stderr)
	for scanner.Scan() {
		fmt.Println(scanner.Text())
	}
	if err := scanner.Err(); err != nil {
		log.Printf("Error: %v\n", err)
	}
	if err := cmd.Wait(); err != nil {
		log.Printf("Error: %v\n", err)
		return err
	}
	return nil
}

// validate
func (a *App) CheckFileExists(path string) error {
	fmt.Printf("check path exists: %s\n", path)
	path = strings.TrimSpace(path)
	if strings.Contains(path, "*") {
		matches, err := filepath.Glob(path)
		if err != nil {
			return err
		}
		if len(matches) == 0 {
			return errors.New("未匹配到任何文件")
		}
		return nil
	}
	if !filepath.IsAbs(path) {
		return errors.New("路径必须是绝对路径!")
	}
	if _, err := os.Stat(path); os.IsNotExist(err) {
		return errors.New("路径不存在!")
	}
	if info, err := os.Stat(path); err == nil && info.IsDir() {
		return errors.New("路径是目录!")
	}
	return nil
}

func (a *App) CheckRangeFormat(pages string) error {
	fmt.Printf("check range: %s\n", pages)
	pages = strings.TrimSpace(pages)
	parts := strings.Split(pages, ",")
	pos_count, neg_count := 0, 0
	for _, part := range parts {
		pattern := regexp.MustCompile(`^!?(\d+|N)(\-(\d+|N))?$`)
		part = strings.TrimSpace(part)
		if !pattern.MatchString(part) {
			return errors.New("页码格式错误!,示例：1-3,5,6-N")
		}
		if part[0] == '!' {
			neg_count++
		} else {
			pos_count++
		}
	}
	if pos_count > 0 && neg_count > 0 {
		return errors.New("不能同时使用正向选择和反向选择!")
	}
	return nil
}

// Golang method

// python method for compress
// func (a *App) CompressPDF(inFile string, outFile string) error {
// 	fmt.Printf("inFile: %s, outFile: %s\n", inFile, outFile)
// 	args := []string{"compress"}
// 	if outFile != "" {
// 		args = append(args, "-o", outFile)
// 	}
// 	args = append(args, inFile)
// 	fmt.Println(args)
// 	cmd := exec.Command(pdfExePath, args...)
// 	err := CheckCmdError(cmd)
// 	if err != nil {
// 		return err
// 	}
// 	return nil
// }

func (a *App) CompressPDF(inFile string, outFile string) error {
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		fmt.Println(err)
		return err
	}
	conf := model.NewDefaultConfiguration()
	if outFile == "" {
		parent := filepath.Dir(inFile)
		fileExt := filepath.Ext(inFile)
		fileName := filepath.Base(inFile)
		fileNameWithoutExt := fileName[:len(fileName)-len(fileExt)]
		outFile = filepath.Join(parent, fileNameWithoutExt+"_压缩.pdf")
	}
	err := api.OptimizeFile(inFile, outFile, conf)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) ConvertPDF(inFile string, outFile string, dstFormat string, pageStr string) error {
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		fmt.Println(err)
		return err
	}
	if outFile == "" {
		outFile = filepath.Dir(inFile)
	}
	if _, err := os.Stat(outFile); os.IsNotExist(err) {
		err = os.MkdirAll(outFile, os.ModePerm)
		if err != nil {
			return err
		}
	}
	err := os.Chdir(outFile)
	if err != nil {
		fmt.Println("切换工作目录错误：", err)
		return err
	}
	fmt.Println(outFile)
	path, _ := os.Getwd()
	fmt.Println(path)
	cmd := exec.Command("C:\\Users\\kevin\\code\\wails_demo\\gui_project\\thirdparty\\mutool.exe", "convert", "-F", dstFormat, inFile, pageStr)
	output, err := cmd.Output()
	if err != nil {
		fmt.Println(err)
		return err
	}
	fmt.Println(string(output))

	return nil
}

// Python method
func (a *App) SplitPDFByChunk(inFile string, chunkSize int, outDir string) error {
	fmt.Printf("inFile: %s, chunkSize: %d, outDir: %s\n", inFile, chunkSize, outDir)
	args := []string{"split", "--mode", "chunk"}
	args = append(args, "--chunk_size")
	args = append(args, fmt.Sprintf("%d", chunkSize))
	if outDir != "" {
		args = append(args, "--output", outDir)
	}
	args = append(args, inFile)
	fmt.Printf("%v\n", args)
	fmt.Println(strings.Join(args, ","))
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) SplitPDFByBookmark(inFile string, tocLevel string, outDir string) error {
	fmt.Printf("inFile: %s, outDir: %s\n", inFile, outDir)
	args := []string{"split", "--mode", "toc"}
	if tocLevel != "" {
		args = append(args, "--toc-level", tocLevel)
	}
	if outDir != "" {
		args = append(args, "--output", outDir)
	}
	args = append(args, inFile)
	fmt.Printf("%v\n", args)
	fmt.Println(strings.Join(args, ","))
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) SplitPDFByPage(inFile string, pages string, outDir string) error {
	fmt.Printf("inFile: %s, pages: %s, outDir: %s\n", inFile, pages, outDir)
	args := []string{"split", "--mode", "page"}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outDir != "" {
		args = append(args, "--output", outDir)
	}
	args = append(args, inFile)
	fmt.Printf("%v\n", args)
	fmt.Println(strings.Join(args, ","))
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) DeletePDF(inFile string, outFile string, pagesStr string) error {
	fmt.Printf("inFile: %s, outFile: %s, pagesStr: %s\n", inFile, outFile, pagesStr)
	args := []string{"delete"}
	if pagesStr != "" {
		args = append(args, "--page_range", pagesStr)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	fmt.Printf("%v\n", args)
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) InsertPDF(inFile1 string, inFile2 string, insertPos int, dstPages string, outFile string) error {
	fmt.Printf("inFile1: %s, inFile2: %s, insertPos: %d, dstPages: %s, outFile: %s\n", inFile1, inFile2, insertPos, dstPages, outFile)
	args := []string{"insert"}
	if insertPos != 0 {
		args = append(args, "--insert_pos", fmt.Sprintf("%d", insertPos))
	}
	if dstPages != "" {
		args = append(args, "--page_range", dstPages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile1)
	args = append(args, inFile2)
	fmt.Printf("%v\n", args)
	fmt.Println(strings.Join(args, ","))
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) InsertBlankPDF(inFile string, outFile string, insertPos int, paper_size string, orientation string, count int) error {
	fmt.Printf("inFile: %s, outFile: %s, insertPos: %d, orientation: %s, count: %d\n", inFile, outFile, insertPos, orientation, count)
	args := []string{"insert", "--method", "blank"}
	args = append(args, "--insert_pos", fmt.Sprintf("%d", insertPos))
	if paper_size != "" {
		args = append(args, "--paper_size", paper_size)
	}
	if orientation != "" {
		args = append(args, "--orientation", orientation)
	}
	args = append(args, "--count", fmt.Sprintf("%d", count))
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile, "placeholder.pdf")
	fmt.Printf("%v\n", args)
	fmt.Println(strings.Join(args, ","))
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) ReplacePDF(inFile1 string, inFile2 string, srcPages string, dstPages string, outFile string) error {
	fmt.Printf("inFile1: %s, inFile2: %s, srcPages: %s, dstPages: %s, outFile: %s\n", inFile1, inFile2, srcPages, dstPages, outFile)
	args := []string{"replace"}
	if srcPages != "" {
		args = append(args, "--src_page_range", srcPages)
	}
	if dstPages != "" {
		args = append(args, "--dst_page_range", dstPages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile1)
	args = append(args, inFile2)
	fmt.Printf("%v\n", args)
	fmt.Println(strings.Join(args, ","))
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) RotatePDF(inFile string, outFile string, rotation int, pagesStr string) error {
	fmt.Printf("inFile: %s, outFile: %s, rotation: %d, pagesStr: %s\n", inFile, outFile, rotation, pagesStr)
	args := []string{"rotate"}
	if rotation != 0 {
		args = append(args, "--angle", fmt.Sprintf("%d", rotation))
	}
	if pagesStr != "" {
		args = append(args, "--page_range", pagesStr)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	fmt.Printf("%v\n", args)
	fmt.Println(strings.Join(args, ","))
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) ReorderPDF(inFile string, outFile string, pagesStr string) error {
	fmt.Printf("inFile: %s, outFile: %s, pagesStr: %s\n", inFile, outFile, pagesStr)
	args := []string{"reorder"}
	if pagesStr != "" {
		args = append(args, "--page_range", pagesStr)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	fmt.Printf("%v\n", args)
	fmt.Println(strings.Join(args, ","))
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) MergePDF(inFiles []string, outFile string, sortMethod string, sortDirection string) error {
	if len(inFiles) == 0 {
		return errors.New("no input files")
	}
	args := []string{"merge"}
	if sortMethod != "" {
		args = append(args, "--sort_method", sortMethod)
	}
	if sortDirection != "" {
		args = append(args, "--sort_direction", sortDirection)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFiles...)
	fmt.Printf("%v\n", args)
	fmt.Println(strings.Join(args, ","))
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) ScalePDFByPaperSize(inFile string, outFile string, paperSize string, pagesStr string) error {
	fmt.Printf("inFile: %s, outFile: %s, paperSize: %s, pagesStr: %s\n", inFile, outFile, paperSize, pagesStr)
	args := []string{"resize", "--method", "paper_size"}
	if paperSize != "" {
		args = append(args, "--paper_size", paperSize)
	}
	if pagesStr != "" {
		args = append(args, "--page_range", pagesStr)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	fmt.Println(args)
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		fmt.Println(err)
		return err
	}
	return nil
}
func (a *App) ScalePDFByScale(inFile string, outFile string, scale float32, pagesStr string) error {
	fmt.Printf("inFile: %s, outFile: %s, scale: %f, pagesStr: %s\n", inFile, outFile, scale, pagesStr)
	args := []string{"resize", "--method", "scale"}
	args = append(args, "--scale", fmt.Sprintf("%f", scale))
	if pagesStr != "" {
		args = append(args, "--page_range", pagesStr)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	fmt.Println(args)
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		fmt.Println(err)
		return err
	}
	return nil
}
func (a *App) ScalePDFByDim(inFile string, outFile string, width float32, height float32, pagesStr string) error {
	fmt.Printf("inFile: %s, outFile: %s, width: %f, height: %f, pagesStr: %s\n", inFile, outFile, width, height, pagesStr)
	args := []string{"resize", "--method", "dim"}
	args = append(args, "--width", fmt.Sprintf("%f", width))
	args = append(args, "--height", fmt.Sprintf("%f", height))
	if pagesStr != "" {
		args = append(args, "--page_range", pagesStr)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	fmt.Println(args)
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		fmt.Println(err)
		return err
	}
	return nil
}

func (a *App) EncryptPDF(inFile string, outFile string, upw string, opw string, perm []string) error {
	fmt.Printf("inFile: %s, outFile: %s, upw: %s, opw: %s, perm: %v\n", inFile, outFile, upw, opw, perm)
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		fmt.Println(err)
		return err
	}
	args := []string{"encrypt"}
	if len(perm) > 0 {
		args = append(args, "--perm")
		args = append(args, perm...)
	}
	if upw != "" {
		args = append(args, "--user_password", upw)
	}
	if opw != "" {
		args = append(args, "--owner_password", opw)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	fmt.Printf("%v\n", args)
	fmt.Println(strings.Join(args, ","))
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) DecryptPDF(inFile string, outFile string, passwd string) error {
	fmt.Printf("inFile: %s, outFile: %s, passwd: %s\n", inFile, outFile, passwd)
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		fmt.Println(err)
		return err
	}
	args := []string{"decrypt"}
	if passwd != "" {
		args = append(args, "--password", passwd)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) ExtractBookmark(inFile string, outFile string, format string) error {
	fmt.Printf("inFile: %s, outFile: %s, format: %s\n", inFile, outFile, format)
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		fmt.Println(err)
		return err
	}
	args := []string{"bookmark", "extract"}
	if format != "" {
		args = append(args, "--format", format)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) WriteBookmarkByFile(inFile string, outFile string, tocFile string, offset int) error {
	fmt.Printf("inFile: %s, outFile: %s, tocFile: %s, offset: %d\n", inFile, outFile, tocFile, offset)
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		fmt.Println(err)
		return err
	}
	if _, err := os.Stat(tocFile); os.IsNotExist(err) {
		fmt.Println(err)
		return err
	}
	args := []string{"bookmark", "add"}
	if tocFile != "" {
		args = append(args, "--toc", tocFile)
	}
	if offset != 0 {
		args = append(args, "--offset", fmt.Sprintf("%d", offset))
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) WriteBookmarkByGap(inFile string, outFile string, gap int, format string) error {
	fmt.Printf("inFile: %s, outFile: %s, gap: %d\n", inFile, outFile, gap)
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		fmt.Println(err)
		return err
	}
	args := []string{"bookmark", "add", "--method", "gap"}
	args = append(args, "--gap", fmt.Sprintf("%d", gap))
	if format != "" {
		args = append(args, "--format", format)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) TransformBookmark(inFile string, outFile string, addIndent bool, addOffset int, removeDots bool) error {
	fmt.Printf("inFile: %s, outFile: %s, addIndent: %v, addOffset: %d, removeDots: %v\n", inFile, outFile, addIndent, addOffset, removeDots)
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		fmt.Println(err)
		return err
	}
	args := []string{"bookmark", "transform"}
	if addIndent {
		args = append(args, "--add_indent")
	}
	if addOffset != 0 {
		args = append(args, "--add_offset", fmt.Sprintf("%d", addOffset))
	}
	if removeDots {
		args = append(args, "--remove_trailing_dots")
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, "--toc", inFile)
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		return err
	}
	output, err := cmd.CombinedOutput()
	if err != nil {
		fmt.Println(err)
		return err
	}
	fmt.Println(string(output))
	return nil
}

func (a *App) WatermarkPDF(inFile string, outFile string, markText string, fontFamily string, fontSize int, fontColor string, angle int, space int, opacity float32, quality int) error {
	fmt.Printf("inFile: %s, outFile: %s, markText: %s, fontFamily: %s, fontSize: %d, fontColor: %s, angle: %d, space: %d, opacity: %f, quality: %d\n", inFile, outFile, markText, fontFamily, fontSize, fontColor, angle, space, opacity, quality)
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		fmt.Println(err)
		return err
	}
	args := []string{"watermark"}
	if markText != "" {
		args = append(args, "--mark-text", markText)
	}
	if fontFamily != "" {
		args = append(args, "--font-family", fontFamily)
	}
	if fontColor != "" {
		args = append(args, "--color", fontColor)
	}
	args = append(args, "--font-size", fmt.Sprintf("%d", fontSize))
	args = append(args, "--angle", fmt.Sprintf("%d", angle))
	args = append(args, "--space", fmt.Sprintf("%d", space))
	args = append(args, "--opacity", fmt.Sprintf("%f", opacity))
	args = append(args, "--quality", fmt.Sprintf("%d", quality))
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	fmt.Println(args)
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) OCR(inFile string, outFile string, pages string, lang string, doubleColumn bool) error {
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		fmt.Println(err)
		return err
	}
	args := []string{"C:\\Users\\kevin\\code\\wails_demo\\gui_project\\thirdparty\\ocr.py", "ocr"}
	if lang != "" {
		args = append(args, "--lang", lang)
	}
	if doubleColumn {
		args = append(args, "--use-double-column")
	}
	if pages != "" {
		args = append(args, "--range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	fmt.Println(args)
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.OcrPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) ExtractTextFromPDF(inFile string, outFile string, pages string) error {
	fmt.Printf("inFile: %s, outFile: %s, pages: %s\n", inFile, outFile, pages)
	args := []string{"extract", "--type", "text"}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	fmt.Println(args)
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) ExtractImageFromPDF(inFile string, outFile string, pages string) error {
	fmt.Printf("inFile: %s, outFile: %s, pages: %s\n", inFile, outFile, pages)
	args := []string{"extract", "--type", "image"}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	fmt.Println(args)
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) CutPDFByGrid(inFile string, outFile string, row int, col int, pages string) error {
	fmt.Printf("inFile: %s, outFile: %s, row: %d, col: %d, pages: %s\n", inFile, outFile, row, col, pages)
	args := []string{"cut", "--method", "grid"}
	args = append(args, "--nrow", fmt.Sprintf("%d", row))
	args = append(args, "--ncol", fmt.Sprintf("%d", col))
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	fmt.Println(args)
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) CutPDFByBreakpoints(inFile string, outFile string, HBreakpoints []float32, VBreakpoints []float32, pages string) error {
	fmt.Printf("inFile: %s, outFile: %s, HBreakpoints: %v, VBreakpoints: %v, pages: %s\n", inFile, outFile, HBreakpoints, VBreakpoints, pages)
	args := []string{"cut", "--method", "breakpoints"}
	args = append(args, inFile)
	if len(HBreakpoints) > 0 {
		args = append(args, "--h_breakpoints")
		for _, v := range HBreakpoints {
			args = append(args, fmt.Sprintf("%f", v))
		}
	}
	if len(VBreakpoints) > 0 {
		args = append(args, "--v_breakpoints")
		for _, v := range VBreakpoints {
			args = append(args, fmt.Sprintf("%f", v))
		}
	}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	fmt.Println(args)
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) CombinePDFByGrid(inFile string, outFile string, row int, col int, pages string, paperSize string, orientation string) error {
	fmt.Printf("inFile: %s, outFile: %s, row: %d, col: %d, pages: %s, paperSize: %s, orientation: %s\n", inFile, outFile, row, col, pages, paperSize, orientation)
	args := []string{"combine"}
	args = append(args, "--nrow", fmt.Sprintf("%d", row))
	args = append(args, "--ncol", fmt.Sprintf("%d", col))
	if paperSize != "" {
		args = append(args, "--paper_size", paperSize)
	}
	if orientation != "" {
		args = append(args, "--orientation", orientation)
	}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	fmt.Println(args)
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) CropPDFByBBOX(inFile string, outFile string, bbox []float32, unit string, keepSize bool, pages string) error {
	fmt.Printf("inFile: %s, outFile: %s, bbox: %v, unit: %s, keepSize: %v, pages: %s\n", inFile, outFile, bbox, unit, keepSize, pages)
	args := []string{"crop", "--method", "bbox"}
	args = append(args, "--bbox")
	for _, v := range bbox {
		args = append(args, fmt.Sprintf("%f", v))
	}
	if unit != "" {
		args = append(args, "--unit", unit)
	}
	if keepSize {
		args = append(args, "--keep_size")
	}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	fmt.Println(args)
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) CropPDFByMargin(inFile string, outFile string, margin []float32, unit string, keepSize bool, pages string) error {
	fmt.Printf("inFile: %s, outFile: %s, margin: %v, unit: %s, keepSize: %v, pages: %s\n", inFile, outFile, margin, unit, keepSize, pages)
	args := []string{"crop", "--method", "margin"}
	args = append(args, "--margin")
	for _, v := range margin {
		args = append(args, fmt.Sprintf("%f", v))
	}
	if unit != "" {
		args = append(args, "--unit", unit)
	}
	if keepSize {
		args = append(args, "--keep_size")
	}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	fmt.Println(args)
	config, err := a.LoadConfig()
	if err != nil {
		return err
	}
	cmd := exec.Command(config.PdfPath, args...)
	err = CheckCmdError(cmd)
	if err != nil {
		return err
	}
	return nil
}
