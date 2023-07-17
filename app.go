//go:build windows

package main

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"runtime"
	"strings"
	"syscall"

	"github.com/pdfcpu/pdfcpu/pkg/api"
	"github.com/pdfcpu/pdfcpu/pkg/pdfcpu/model"
	"github.com/pkg/errors"
	wails_runtime "github.com/wailsapp/wails/v2/pkg/runtime"
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
	PdfPath       string `json:"pdf_path"`
	PythonPath    string `json:"python_path"`
	TesseractPath string `json:"tesseract_path"`
	PandocPath    string `json:"pandoc_path"`
	HashcatPath   string `json:"hashcat_path"`
}

type CmdOutput struct {
	Status  string `json:"status"`
	Message string `json:"message"`
}

func (a *App) SelectFile() string {
	d, err := wails_runtime.OpenFileDialog(a.ctx, wails_runtime.OpenDialogOptions{})
	if err != nil {
		logger.Errorln(err)
		return ""
	}
	logger.Debugf("%v\n", d)
	return d
}

func (a *App) SelectMultipleFiles() []string {
	d, err := wails_runtime.OpenMultipleFilesDialog(a.ctx, wails_runtime.OpenDialogOptions{})
	if err != nil {
		logger.Errorln(err)
		return nil
	}
	logger.Debugf("%v\n", d)
	return d
}

func (a *App) SelectDir() string {
	d, err := wails_runtime.OpenDirectoryDialog(a.ctx, wails_runtime.OpenDialogOptions{})
	if err != nil {
		logger.Errorln(err)
		return ""
	}
	logger.Debugf("%v\n", d)
	return d
}

func (a *App) SaveFile() string {
	d, err := wails_runtime.SaveFileDialog(a.ctx, wails_runtime.SaveDialogOptions{})
	if err != nil {
		logger.Errorln(err)
		return ""
	}
	logger.Debugf("%v\n", d)
	return d
}

func (a *App) OpenUrl(url string) {
	wails_runtime.BrowserOpenURL(a.ctx, url)
}

func (a *App) SaveConfig(pdfPath string, pythonPath string, tesseractPath string, pandocPath string, hashcatPath string) error {
	var config MyConfig
	config.PdfPath = pdfPath
	config.PythonPath = pythonPath
	config.TesseractPath = tesseractPath
	config.PandocPath = pandocPath
	config.HashcatPath = hashcatPath
	log.Printf("%v\n", config)
	jsonData, err := json.Marshal(config)
	if err != nil {
		err = errors.Wrap(err, "marshal config error")
		logger.Errorln(err)
		return err
	}
	// 获取配置文件路径
	path, err := os.Executable()
	if err != nil {
		err = errors.Wrap(err, "")
		logger.Errorln("Error:", err)
		return err
	}

	configPath := filepath.Join(filepath.Dir(path), "config.json")
	if runtime.GOOS == "darwin" {
		configPath = filepath.Join(filepath.Dir(filepath.Dir(filepath.Dir(filepath.Dir(path)))), "config.json")
	} else if runtime.GOOS == "linux" {
		configPath = filepath.Join(filepath.Dir(path), "config.json")
	}
	err = os.WriteFile(configPath, jsonData, 0644)
	if err != nil {
		err = errors.Wrap(err, "")
		logger.Errorln("Error:", err)
		return err
	}
	return nil
}

func (a *App) LoadConfig() (MyConfig, error) {
	var config MyConfig

	// 获取配置文件路径
	path, err := os.Executable()
	if err != nil {
		err = errors.Wrap(err, "")
		logger.Errorln("Error:", err)
		return config, err
	}

	configPath := filepath.Join(filepath.Dir(path), "config.json")
	if runtime.GOOS == "darwin" {
		configPath = filepath.Join(filepath.Dir(filepath.Dir(filepath.Dir(filepath.Dir(path)))), "config.json")
	}
	if _, err := os.Stat(configPath); os.IsNotExist(err) {
		path, err := os.Executable()
		if err != nil {
			err = errors.Wrap(err, "")
			logger.Errorln("Error:", err)
			return config, err
		}
		pdfPath := filepath.Join(filepath.Dir(path), "pdf.exe")
		if runtime.GOOS == "darwin" {
			pdfPath = filepath.Join(filepath.Dir(filepath.Dir(filepath.Dir(filepath.Dir(path)))), "pdf")
		} else if runtime.GOOS == "linux" {
			pdfPath = filepath.Join(filepath.Dir(path), "pdf")
		}
		err = a.SaveConfig(pdfPath, "", "", "", "")
		if err != nil {
			err = errors.Wrap(err, "")
			return config, err
		}
	}
	data, err := os.ReadFile(configPath)
	if err != nil {
		err = errors.Wrap(err, "")
		return config, err
	}
	err = json.Unmarshal(data, &config)
	if err != nil {
		err = errors.Wrap(err, "")
		return config, err
	}
	return config, nil
}

func CheckCmdError(cmd *exec.Cmd) error {
	stderr, err := cmd.StderrPipe()
	if err != nil {
		err = errors.Wrap(err, "")
		err = errors.Wrap(err, "")
		logger.Errorf("Error: %v\n", err)
		return err
	}
	if err := cmd.Start(); err != nil {
		logger.Errorf("Error: %v\n", err)
		return err
	}
	scanner := bufio.NewScanner(stderr)
	for scanner.Scan() {
		logger.Println(scanner.Text())
	}
	if err := scanner.Err(); err != nil {
		logger.Errorf("Error: %v\n", err)
	}
	if err := cmd.Wait(); err != nil {
		logger.Errorf("Error: %v\n", err)
		return err
	}
	return nil
}

func GetCmdStatusAndMessage(cmd *exec.Cmd) error {
	defer func() {
		if err := recover(); err != nil {
			logger.Fatalln(err)
		}
	}()
	if runtime.GOOS == "windows" {
		cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
	}
	out, err := cmd.Output()
	if err != nil {
		err = errors.Wrap(err, "get cmd output error! \n args: "+strings.Join(cmd.Args, " ")+"\n stderr: "+string(err.(*exec.ExitError).Stderr))
		logger.Errorln("Error:", err)
		return err
	}
	logger.Println(string(out))

	ret_path := filepath.Join(logdir, "cmd_output.json")
	var ret CmdOutput
	data, err := os.ReadFile(ret_path)
	if err != nil {
		err = errors.Wrap(err, "read cmd output file error")
		return err
	}
	err = json.Unmarshal(data, &ret)
	if err != nil {
		err = errors.Wrap(err, "json umarshal error")
		return err
	}

	if ret.Status != "success" {
		logger.Errorf("Error: %v\n", ret.Message)
		return errors.New(ret.Message)
	}
	return nil
}

func (a *App) cmdRunner(args []string, cmdType string) error {
	config, err := a.LoadConfig()
	if err != nil {
		err = errors.Wrap(err, "")
		return err
	}
	var cmd *exec.Cmd
	if cmdType == "pdf" {
		cmd = exec.Command(config.PdfPath, args...)
	} else if cmdType == "python" {
		cmd = exec.Command(config.PythonPath, args...)
	} else if cmdType == "pandoc" {
		cmd = exec.Command(config.PandocPath, args...)
	} else if cmdType == "tesseract" {
		cmd = exec.Command(config.TesseractPath, args...)
	} else if cmdType == "hashcat" {
		cmd = exec.Command(config.HashcatPath, args...)
	} else {
		err = errors.Wrap(err, "unsupport cmd type!")
		return err
	}
	err = GetCmdStatusAndMessage(cmd)
	if err != nil {
		err = errors.Wrap(err, "")
		return err
	}
	return nil
}

func (a *App) CheckOS() string {
	return runtime.GOOS
}

// validate
func (a *App) CheckFileExists(path string) error {
	path = strings.TrimSpace(path)
	if strings.Contains(path, "*") {
		matches, err := filepath.Glob(path)
		if err != nil {
			err = errors.Wrap(err, "")
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

func (a *App) CheckOutputDirExists(path string) error {
	if !filepath.IsAbs(path) {
		return errors.New("路径必须是绝对路径!")
	}
	if info, err := os.Stat(path); err == nil && !info.IsDir() {
		return errors.New("路径是文件，不是目录!")
	}
	if _, err := os.Stat(path); os.IsNotExist(err) {
		return errors.New("路径不存在，继续则自动创建目录!")
	}
	return nil
}

func (a *App) CheckOutputFileExists(path string) error {
	if !filepath.IsAbs(path) {
		return errors.New("路径必须是绝对路径!")
	}
	if info, err := os.Stat(path); err == nil {
		if info.IsDir() {
			return errors.New("路径是目录，不是文件!")
		}
		return errors.New("路径已存在，继续则覆盖文件!")
	}
	return nil
}

func (a *App) CheckRangeFormat(pages string) error {
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
// 	logger.Printf("inFile: %s, outFile: %s\n", inFile, outFile)
// 	args := []string{"compress"}
// 	if outFile != "" {
// 		args = append(args, "-o", outFile)
// 	}
// 	args = append(args, inFile)
// 	logger.Println(args)
// 	cmd := exec.Command(pdfExePath, args...)
// 	err := CheckCmdError(cmd)
// 	if err != nil {
// err = errors.Wrap(err, "")
// 		return err
// 	}
// 	return nil
// }

func (a *App) CompressPDF(inFile string, outFile string) error {
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		logger.Errorln(err)
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
		err = errors.Wrap(err, "")
		return err
	}
	return nil
}

// Python method
func (a *App) SplitPDFByChunk(inFile string, chunkSize int, outDir string) error {
	logger.Printf("inFile: %s, chunkSize: %d, outDir: %s\n", inFile, chunkSize, outDir)
	args := []string{"split", "--mode", "chunk"}
	args = append(args, "--chunk_size")
	args = append(args, fmt.Sprintf("%d", chunkSize))
	if outDir != "" {
		args = append(args, "--output", outDir)
	}
	args = append(args, inFile)
	logger.Println(args)

	return a.cmdRunner(args, "pdf")
}

func (a *App) SplitPDFByBookmark(inFile string, tocLevel string, outDir string) error {
	logger.Printf("inFile: %s, outDir: %s\n", inFile, outDir)
	args := []string{"split", "--mode", "toc"}
	if tocLevel != "" {
		args = append(args, "--toc-level", tocLevel)
	}
	if outDir != "" {
		args = append(args, "--output", outDir)
	}
	args = append(args, inFile)
	logger.Println(args)

	return a.cmdRunner(args, "pdf")
}

func (a *App) SplitPDFByPage(inFile string, pages string, outDir string) error {
	logger.Printf("inFile: %s, pages: %s, outDir: %s\n", inFile, pages, outDir)
	args := []string{"split", "--mode", "page"}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outDir != "" {
		args = append(args, "--output", outDir)
	}
	args = append(args, inFile)
	logger.Println(args)

	return a.cmdRunner(args, "pdf")
}

func (a *App) DeletePDF(inFile string, outFile string, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, pages: %s\n", inFile, outFile, pages)
	args := []string{"delete"}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) InsertPDF(inFile1 string, inFile2 string, insertPos int, dstPages string, posType string, outFile string) error {
	logger.Printf("inFile1: %s, inFile2: %s, insertPos: %d, dstPages: %s, posType: %s, outFile: %s\n", inFile1, inFile2, insertPos, dstPages, posType, outFile)
	args := []string{"insert"}
	if insertPos != 0 {
		args = append(args, "--insert_pos", fmt.Sprintf("%d", insertPos))
	}
	if posType != "" {
		args = append(args, "--pos-type", posType)
	}
	if dstPages != "" {
		args = append(args, "--page_range", dstPages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile1)
	args = append(args, inFile2)
	logger.Println(args)

	return a.cmdRunner(args, "pdf")
}

func (a *App) InsertBlankPDF(inFile string, outFile string, insertPos int, posType string, paper_size string, orientation string, count int) error {
	logger.Printf("inFile: %s, outFile: %s, insertPos: %d, posType: %s, paper_size: %s, orientation: %s, count: %d\n", inFile, outFile, insertPos, posType, paper_size, orientation, count)
	args := []string{"insert", "--method", "blank"}
	args = append(args, "--insert_pos", fmt.Sprintf("%d", insertPos))
	if posType != "" {
		args = append(args, "--pos-type", posType)
	}
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
	logger.Println(args)

	return a.cmdRunner(args, "pdf")
}

func (a *App) ReplacePDF(inFile1 string, inFile2 string, srcPages string, dstPages string, outFile string) error {
	logger.Printf("inFile1: %s, inFile2: %s, srcPages: %s, dstPages: %s, outFile: %s\n", inFile1, inFile2, srcPages, dstPages, outFile)
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
	logger.Println(args)

	return a.cmdRunner(args, "pdf")
}

func (a *App) RotatePDF(inFile string, outFile string, rotation int, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, rotation: %d, pages: %s\n", inFile, outFile, rotation, pages)
	args := []string{"rotate"}
	if rotation != 0 {
		args = append(args, "--angle", fmt.Sprintf("%d", rotation))
	}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)

	return a.cmdRunner(args, "pdf")
}

func (a *App) ReorderPDF(inFile string, outFile string, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, pages: %s\n", inFile, outFile, pages)
	args := []string{"reorder"}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)

	return a.cmdRunner(args, "pdf")
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
	logger.Println(args)

	return a.cmdRunner(args, "pdf")
}

func (a *App) ScalePDFByPaperSize(inFile string, outFile string, paperSize string, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, paperSize: %s, pages: %s\n", inFile, outFile, paperSize, pages)
	args := []string{"resize", "--method", "paper_size"}
	if paperSize != "" {
		args = append(args, "--paper_size", paperSize)
	}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}
func (a *App) ScalePDFByScale(inFile string, outFile string, scale float32, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, scale: %f, pages: %s\n", inFile, outFile, scale, pages)
	args := []string{"resize", "--method", "scale"}
	args = append(args, "--scale", fmt.Sprintf("%f", scale))
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) ScalePDFByDim(inFile string, outFile string, width float32, height float32, unit string, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, width: %f, height: %f, unit: %s, pages: %s\n", inFile, outFile, width, height, unit, pages)
	args := []string{"resize", "--method", "dim"}
	args = append(args, "--width", fmt.Sprintf("%f", width))
	args = append(args, "--height", fmt.Sprintf("%f", height))
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if unit != "" {
		args = append(args, "--unit", unit)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) EncryptPDF(inFile string, outFile string, upw string, opw string, perm []string) error {
	logger.Printf("inFile: %s, outFile: %s, upw: %s, opw: %s, perm: %v\n", inFile, outFile, upw, opw, perm)
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		logger.Errorln(err)
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
	logger.Println(args)

	return a.cmdRunner(args, "pdf")
}

func (a *App) DecryptPDF(inFile string, outFile string, passwd string) error {
	logger.Printf("inFile: %s, outFile: %s, passwd: %s\n", inFile, outFile, passwd)
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		logger.Errorln(err)
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
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) ExtractBookmark(inFile string, outFile string, format string) error {
	logger.Printf("inFile: %s, outFile: %s, format: %s\n", inFile, outFile, format)
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		logger.Errorln(err)
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
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) WriteBookmarkByFile(inFile string, outFile string, tocFile string, offset int) error {
	logger.Printf("inFile: %s, outFile: %s, tocFile: %s, offset: %d\n", inFile, outFile, tocFile, offset)
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		logger.Errorln(err)
		return err
	}
	if _, err := os.Stat(tocFile); os.IsNotExist(err) {
		logger.Errorln(err)
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
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) WriteBookmarkByGap(inFile string, outFile string, gap int, format string, startNumber int, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, gap: %d\n", inFile, outFile, gap)
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		logger.Errorln(err)
		return err
	}
	args := []string{"bookmark", "add", "--method", "gap"}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	args = append(args, "--start-number", fmt.Sprintf("%d", startNumber))
	args = append(args, "--gap", fmt.Sprintf("%d", gap))
	if format != "" {
		args = append(args, "--format", format)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) TransformBookmark(inFile string, outFile string, addOffset int, levelDict []string, deleteLevelBelow int, defaultLevel int, isRemoveBlankLines bool) error {
	logger.Printf("inFile: %s, outFile: %s, addOffset: %d, levelDict: %v, deleteLevelBelow: %d\n", inFile, outFile, addOffset, levelDict, deleteLevelBelow)
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		logger.Errorln(err)
		return err
	}
	args := []string{"bookmark", "transform"}
	args = append(args, "--delete-level-below", fmt.Sprintf("%d", deleteLevelBelow))
	for _, level := range levelDict {
		args = append(args, "--level-dict", level)
	}
	if addOffset != 0 {
		args = append(args, "--add_offset", fmt.Sprintf("%d", addOffset))
	}
	args = append(args, "--default-level", fmt.Sprintf("%d", defaultLevel))
	if isRemoveBlankLines {
		args = append(args, "--remove-blank-lines")
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, "--toc", inFile)
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) DetectBookmarkByFont(
	inFile string,
	outFile string,
	pages string) error {
	logger.Printf("inFile: %s, outFile: %s, pages: %s\n", inFile, outFile, pages)
	args := []string{"bookmark", "detect"}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) WatermarkPDFByText(inFile string, outFile string, markText string, fontFamily string, fontSize int, fontColor string, angle int, opacity float32, num_lines int, line_spacing float32, word_spacing float32, x_offset float32, y_offset float32, multiple_mode bool, layer string, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, markText: %s, fontFamily: %s, fontSize: %d, fontColor: %s, angle: %d, opacity: %f, num_lines: %d, line_spacing: %f, word_spacing: %f, x_offset: %f, y_offset: %f, multiple_mode: %v, layer: %s\n", inFile, outFile, markText, fontFamily, fontSize, fontColor, angle, opacity, num_lines, line_spacing, word_spacing, x_offset, y_offset, multiple_mode, layer)
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		logger.Errorln(err)
		return err
	}
	args := []string{"watermark", "add"}
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
	args = append(args, "--opacity", fmt.Sprintf("%f", opacity))
	args = append(args, "--num-lines", fmt.Sprintf("%d", num_lines))
	args = append(args, "--line-spacing", fmt.Sprintf("%f", line_spacing))
	args = append(args, "--word-spacing", fmt.Sprintf("%f", word_spacing))
	args = append(args, "--x-offset", fmt.Sprintf("%f", x_offset))
	args = append(args, "--y-offset", fmt.Sprintf("%f", y_offset))
	if multiple_mode {
		args = append(args, "--multiple-mode")
	}
	if layer != "" {
		args = append(args, "--layer", layer)
	}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) WatermarkPDFByImage(inFile string, outFile string, wmPath string, angle int, opacity float32, scale float32, num_lines int, line_spacing float32, word_spacing float32, x_offset float32, y_offset float32, multiple_mode bool, layer string, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, wmPath: %s, angle: %d, opacity: %f, scale: %f, num_lines: %d, line_spacing: %f, word_spacing: %f, x_offset: %f, y_offset: %f, multiple_mode: %v, layer: %s\n", inFile, outFile, wmPath, angle, opacity, scale, num_lines, line_spacing, word_spacing, x_offset, y_offset, multiple_mode, layer)
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		logger.Errorln(err)
		return err
	}
	args := []string{"watermark", "add", "--type", "image"}
	if wmPath != "" {
		args = append(args, "--wm-path", wmPath)
	}
	args = append(args, "--angle", fmt.Sprintf("%d", angle))
	args = append(args, "--opacity", fmt.Sprintf("%f", opacity))
	args = append(args, "--scale", fmt.Sprintf("%f", scale))
	args = append(args, "--num-lines", fmt.Sprintf("%d", num_lines))
	args = append(args, "--line-spacing", fmt.Sprintf("%f", line_spacing))
	args = append(args, "--word-spacing", fmt.Sprintf("%f", word_spacing))
	args = append(args, "--x-offset", fmt.Sprintf("%f", x_offset))
	args = append(args, "--y-offset", fmt.Sprintf("%f", y_offset))
	if multiple_mode {
		args = append(args, "--multiple-mode")
	}
	if layer != "" {
		args = append(args, "--layer", layer)
	}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) WatermarkPDFByPDF(inFile string, outFile string, wmPath string, layer string, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, wmPath: %s, layer: %s\n", inFile, outFile, wmPath, layer)
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		logger.Errorln(err)
		return err
	}
	args := []string{"watermark", "add", "--type", "pdf"}
	if wmPath != "" {
		args = append(args, "--wm-path", wmPath)
	}
	if layer != "" {
		args = append(args, "--layer", layer)
	}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) OCR(inFile string, outFile string, pages string, lang string, doubleColumn bool) error {
	logger.Printf("inFile: %s, outFile: %s, pages: %s, lang: %s, doubleColumn: %v\n", inFile, outFile, pages, lang, doubleColumn)
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		logger.Errorln(err)
		return err
	}
	// path := filepath.Join(tmpDir, "ocr.py")
	path, err := os.Executable()
	if err != nil {
		logger.Errorln(err)
		return err
	}
	path = filepath.Join(filepath.Dir(path), "ocr.py")
	args := []string{path, "ocr"}
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
	logger.Println(args)
	return a.cmdRunner(args, "python")
}

func (a *App) OCRPDFBookmark(inFile string, outFile string, pages string, lang string, doubleColumn bool) error {
	logger.Printf("inFile: %s, outFile: %s, pages: %s, lang: %s, doubleColumn: %v\n", inFile, outFile, pages, lang, doubleColumn)
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		logger.Errorln(err)
		return err
	}
	// path := filepath.Join(tmpDir, "ocr.py")
	path, err := os.Executable()
	if err != nil {
		logger.Errorln(err)
		return err
	}
	path = filepath.Join(filepath.Dir(path), "ocr.py")
	args := []string{path, "bookmark"}
	if lang != "" {
		args = append(args, "--lang", lang)
	}
	if doubleColumn {
		args = append(args, "--double-column")
	}
	if pages != "" {
		args = append(args, "--range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)
	return a.cmdRunner(args, "python")
}

func (a *App) OCRExtract(inFile string, outFile string, pages string, extractType string) error {
	logger.Printf("inFile: %s, outFile: %s, pages: %s, extractType: %s\n", inFile, outFile, pages, extractType)
	args := []string{"ocr", "extract"}
	if extractType != "" {
		args = append(args, "--type", extractType)
	}
	if pages != "" {
		args = append(args, "--range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)
	return a.cmdRunner(args, "python")
}

func (a *App) ExtractTextFromPDF(inFile string, outFile string, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, pages: %s\n", inFile, outFile, pages)
	args := []string{"extract", "--type", "text"}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) ExtractImageFromPDF(inFile string, outFile string, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, pages: %s\n", inFile, outFile, pages)
	args := []string{"extract", "--type", "image"}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) CutPDFByGrid(inFile string, outFile string, row int, col int, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, row: %d, col: %d, pages: %s\n", inFile, outFile, row, col, pages)
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
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) CutPDFByBreakpoints(inFile string, outFile string, HBreakpoints []float32, VBreakpoints []float32, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, HBreakpoints: %v, VBreakpoints: %v, pages: %s\n", inFile, outFile, HBreakpoints, VBreakpoints, pages)
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
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) CombinePDFByGrid(inFile string, outFile string, row int, col int, pages string, paperSize string, orientation string) error {
	logger.Printf("inFile: %s, outFile: %s, row: %d, col: %d, pages: %s, paperSize: %s, orientation: %s\n", inFile, outFile, row, col, pages, paperSize, orientation)
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
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) CropPDFByBBOX(inFile string, outFile string, bbox []float32, unit string, keepSize bool, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, bbox: %v, unit: %s, keepSize: %v, pages: %s\n", inFile, outFile, bbox, unit, keepSize, pages)
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
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) CropPDFByMargin(inFile string, outFile string, margin []float32, unit string, keepSize bool, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, margin: %v, unit: %s, keepSize: %v, pages: %s\n", inFile, outFile, margin, unit, keepSize, pages)
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
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) RemoveWatermarkByType(inFile string, outFile string, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, pages: %s\n", inFile, outFile, pages)
	args := []string{"watermark", "remove", "--method", "type"}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) RemoveWatermarkByIndex(inFile string, outFile string, wmIndex []int, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, wmIndex: %v, pages: %s\n", inFile, outFile, wmIndex, pages)
	args := []string{"watermark", "remove"}
	args = append(args, inFile)
	args = append(args, "--method", "index")
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	args = append(args, "--wm_index")
	for _, v := range wmIndex {
		args = append(args, fmt.Sprintf("%d", v))
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) DetectWatermarkByIndex(inFile string, outFile string, wmIndex int) error {
	logger.Printf("inFile: %s, outFile: %s, wmIndex: %d\n", inFile, outFile, wmIndex)
	args := []string{"watermark", "detect"}
	args = append(args, inFile)
	args = append(args, "--wm_index")
	args = append(args, fmt.Sprintf("%d", wmIndex))
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) MaskPDFByRect(inFile string, outFile string, rect []float32, unit string, color string, opacity float32, angle float32, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, rect: %v, unit: %s, color: %s, opacity: %f, angle: %f, pages: %s\n", inFile, outFile, rect, unit, color, opacity, angle, pages)
	args := []string{"mask", "--type", "rect"}
	args = append(args, "--bbox")
	for _, v := range rect {
		args = append(args, fmt.Sprintf("%f", v))
	}
	if unit != "" {
		args = append(args, "--unit", unit)
	}
	if color != "" {
		args = append(args, "--color", color)
	}
	args = append(args, "--opacity", fmt.Sprintf("%f", opacity))
	args = append(args, "--angle", fmt.Sprintf("%f", angle))
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)

	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) MaskPDFByAnnot(inFile string, outFile string, annot_page int, color string, opacity float32, angle float32, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, annot_page: %d, color: %s, opacity: %f, angle: %f, pages: %s\n", inFile, outFile, annot_page, color, opacity, angle, pages)
	args := []string{"mask", "--type", "annot"}
	args = append(args, "--annot-page", fmt.Sprintf("%d", annot_page))
	if color != "" {
		args = append(args, "--color", color)
	}
	args = append(args, "--opacity", fmt.Sprintf("%f", opacity))
	args = append(args, "--angle", fmt.Sprintf("%f", angle))
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)

	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) AddPDFBackgroundByColor(inFile string, outFile string, color string, opacity float32, angle float32, x_offset float32, y_offset float32, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, color: %s, opacity: %f, angle: %f, x_offset: %f, y_offset: %f, pages: %s\n", inFile, outFile, color, opacity, angle, x_offset, y_offset, pages)
	args := []string{"bg", "--type", "color"}
	if color != "" {
		args = append(args, "--color", color)
	}
	args = append(args, "--opacity", fmt.Sprintf("%f", opacity))
	args = append(args, "--angle", fmt.Sprintf("%f", angle))
	args = append(args, "--x-offset", fmt.Sprintf("%f", x_offset))
	args = append(args, "--y-offset", fmt.Sprintf("%f", y_offset))
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}

	args = append(args, inFile)

	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) AddPDFBackgroundByImage(inFile string, imgFile string, outFile string, opacity float32, angle float32, x_offset float32, y_offset float32, scale float32, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, imgFile: %s, opacity: %f, angle: %f, x_offset: %f, y_offset: %f, pages: %s\n", inFile, outFile, imgFile, opacity, angle, x_offset, y_offset, pages)
	args := []string{"bg", "--type", "image"}
	if imgFile != "" {
		args = append(args, "--img-path", imgFile)
	}
	args = append(args, "--opacity", fmt.Sprintf("%f", opacity))
	args = append(args, "--angle", fmt.Sprintf("%f", angle))
	args = append(args, "--x-offset", fmt.Sprintf("%f", x_offset))
	args = append(args, "--y-offset", fmt.Sprintf("%f", y_offset))
	args = append(args, "--scale", fmt.Sprintf("%f", scale))
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}

	args = append(args, inFile)

	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) AddPDFHeaderAndFooter(
	inFile string,
	outFile string,
	header_left string,
	header_center string,
	header_right string,
	footer_left string,
	footer_center string,
	footer_right string,
	margin_bbox []float32,
	unit string,
	font_family string,
	font_size int,
	font_color string,
	opacity float32,
	pages string) error {
	logger.Printf("inFile: %s, outFile: %s, header_left: %s, header_center: %s, header_right: %s, footer_left: %s, footer_center: %s, footer_right: %s, margin_bbox: %v, unit: %s, font_family: %s, font_size: %d, font_color: %s, opacity: %f, pages: %s\n", inFile, outFile, header_left, header_center, header_right, footer_left, footer_center, footer_right, margin_bbox, unit, font_family, font_size, font_color, opacity, pages)
	args := []string{"header_footer", "--type", "add"}
	if header_left != "" {
		args = append(args, "--header-left", header_left)
	}
	if header_center != "" {
		args = append(args, "--header-center", header_center)
	}
	if header_right != "" {
		args = append(args, "--header-right", header_right)
	}
	if footer_left != "" {
		args = append(args, "--footer-left", footer_left)
	}
	if footer_center != "" {
		args = append(args, "--footer-center", footer_center)
	}
	if footer_right != "" {
		args = append(args, "--footer-right", footer_right)
	}
	if len(margin_bbox) > 0 {
		args = append(args, "--margin-bbox")
		for _, v := range margin_bbox {
			args = append(args, fmt.Sprintf("%f", v))
		}
	}
	if unit != "" {
		args = append(args, "--unit", unit)
	}
	if font_family != "" {
		args = append(args, "--font-family", font_family)
	}
	if font_size != 0 {
		args = append(args, "--font-size", fmt.Sprintf("%d", font_size))
	}
	if font_color != "" {
		args = append(args, "--font-color", font_color)
	}
	if opacity != 0 {
		args = append(args, "--opacity", fmt.Sprintf("%f", opacity))
	}
	if pages != "" {
		args = append(args, "--page-range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)

	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) AddPDFPageNumber(
	inFile string,
	outFile string,
	pos string,
	start int,
	format string,
	margin_bbox []float32,
	unit string,
	align string,
	font_family string,
	font_size int,
	font_color string,
	opacity float32,
	pages string) error {
	logger.Printf("inFile: %s, outFile: %s, pos: %s, start: %d, format: %s, margin_bbox: %v, unit: %s, font_family: %s, font_size: %d, font_color: %s, opacity: %f, pages: %s\n", inFile, outFile, pos, start, format, margin_bbox, unit, font_family, font_size, font_color, opacity, pages)
	args := []string{"page_number", "--type", "add"}
	if pos != "" {
		args = append(args, "--pos", pos)
	}
	if start != 0 {
		args = append(args, "--start", fmt.Sprintf("%d", start))
	}
	if format != "" {
		args = append(args, "--format", format)
	}
	if align != "" {
		args = append(args, "--align", align)
	}
	if len(margin_bbox) > 0 {
		args = append(args, "--margin-bbox")
		for _, v := range margin_bbox {
			args = append(args, fmt.Sprintf("%f", v))
		}
	}
	if unit != "" {
		args = append(args, "--unit", unit)
	}
	if font_family != "" {
		args = append(args, "--font-family", font_family)
	}
	if font_size != 0 {
		args = append(args, "--font-size", fmt.Sprintf("%d", font_size))
	}
	if font_color != "" {
		args = append(args, "--font-color", font_color)
	}
	if opacity != 0 {
		args = append(args, "--opacity", fmt.Sprintf("%f", opacity))
	}
	if pages != "" {
		args = append(args, "--page-range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)

	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) RemovePDFHeaderAndFooter(
	inFile string,
	outFile string,
	margin_bbox []float32,
	remove_list []string,
	unit string,
	pages string) error {
	logger.Printf("inFile: %s, outFile: %s, margin_bbox: %v, remove_list: %v, unit: %s, pages: %s\n", inFile, outFile, margin_bbox, remove_list, unit, pages)
	args := []string{"header_footer", "--type", "remove"}
	if len(margin_bbox) > 0 {
		args = append(args, "--margin-bbox")
		for _, v := range margin_bbox {
			args = append(args, fmt.Sprintf("%f", v))
		}
	}
	if len(remove_list) > 0 {
		args = append(args, "--remove")
		args = append(args, remove_list...)
	}
	if unit != "" {
		args = append(args, "--unit", unit)
	}
	if pages != "" {
		args = append(args, "--page-range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)

	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) RemovePDFPageNumber(
	inFile string,
	outFile string,
	margin_bbox []float32,
	pos string,
	unit string,
	pages string) error {
	logger.Printf("inFile: %s, outFile: %s, margin_bbox: %v, pos: %s, unit: %s, pages: %s\n", inFile, outFile, margin_bbox, pos, unit, pages)
	args := []string{"page_number", "--type", "remove"}
	if len(margin_bbox) > 0 {
		args = append(args, "--margin-bbox")
		for _, v := range margin_bbox {
			args = append(args, fmt.Sprintf("%f", v))
		}
	}
	if pos != "" {
		args = append(args, "--pos", pos)
	}
	if unit != "" {
		args = append(args, "--unit", unit)
	}
	if pages != "" {
		args = append(args, "--page-range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)

	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) PDFConversion(
	inFile string,
	outFile string,
	dpi int,
	isMerge bool,
	srcType string,
	dstType string,
	pages string,
	convert_type string) error {
	logger.Printf("inFile: %s, outFile: %s, dpi: %d, srcType: %s, dstType: %s, pages: %s\n", inFile, outFile, dpi, srcType, dstType, pages)
	args := []string{"convert", "--source-type", srcType, "--target-type", dstType}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if (srcType == "pdf" && dstType == "png") || (srcType == "pdf" && dstType == "svg") || (srcType == "pdf" && dstType == "image-pdf") {
		args = append(args, "--dpi", fmt.Sprintf("%d", dpi))
	}
	if isMerge {
		args = append(args, "--is_merge")
	}
	args = append(args, inFile)
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) ConvertPDF2Docx(
	inFile string,
	outFile string,
) error {
	logger.Printf("inFile: %s, outFile: %s\n", inFile, outFile)
	path, err := os.Executable()
	if err != nil {
		err = errors.Wrap(err, "")
		logger.Errorln("Error:", err)
		return err
	}
	path = filepath.Join(filepath.Dir(path), "convert.py")
	args := []string{path, "--source-type", "pdf", "--target-type", "docx"}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)
	return a.cmdRunner(args, "python")
}

// Pandoc convert

func (a *App) ConvertMd2Docx(
	inFile string,
	outFile string,
) error {
	logger.Printf("inFile: %s, outFile: %s\n", inFile, outFile)
	if outFile == "" {
		outFile = strings.TrimSuffix(inFile, filepath.Ext(inFile)) + ".docx"
	}
	args := []string{"-s", inFile, "-o", outFile}
	config, err := a.LoadConfig()
	if err != nil {
		err = errors.Wrap(err, "")
		return err
	}
	cmd := exec.Command(config.PandocPath, args...)

	err = CheckCmdError(cmd)

	if err != nil {
		err = errors.Wrap(err, "")
		return err
	}
	return nil
}

func (a *App) ConvertMd2Tex(
	inFile string,
	outFile string,
) error {
	logger.Printf("inFile: %s, outFile: %s\n", inFile, outFile)
	if outFile == "" {
		outFile = strings.TrimSuffix(inFile, filepath.Ext(inFile)) + ".tex"
	}
	args := []string{"-s", inFile, "-o", outFile}
	config, err := a.LoadConfig()
	if err != nil {
		err = errors.Wrap(err, "")
		return err
	}
	cmd := exec.Command(config.PandocPath, args...)

	err = CheckCmdError(cmd)

	if err != nil {
		err = errors.Wrap(err, "")
		return err
	}
	return nil
}

func (a *App) ConvertMd2Html(
	inFile string,
	outFile string,
) error {
	logger.Printf("inFile: %s, outFile: %s\n", inFile, outFile)
	if outFile == "" {
		outFile = strings.TrimSuffix(inFile, filepath.Ext(inFile)) + ".html"
	}
	args := []string{"-s", inFile, "-o", outFile}
	config, err := a.LoadConfig()
	if err != nil {
		err = errors.Wrap(err, "")
		return err
	}
	cmd := exec.Command(config.PandocPath, args...)

	err = CheckCmdError(cmd)

	if err != nil {
		err = errors.Wrap(err, "")
		return err
	}
	return nil
}

func (a *App) ConvertMd2PDF(
	inFile string,
	outFile string,
) error {
	logger.Printf("inFile: %s, outFile: %s\n", inFile, outFile)
	if outFile == "" {
		outFile = strings.TrimSuffix(inFile, filepath.Ext(inFile)) + ".pdf"
	}
	args := []string{"-s", inFile, "-o", outFile}
	config, err := a.LoadConfig()
	if err != nil {
		err = errors.Wrap(err, "")
		return err
	}
	cmd := exec.Command(config.PandocPath, args...)

	err = CheckCmdError(cmd)

	if err != nil {
		err = errors.Wrap(err, "")
		return err
	}
	return nil
}

func (a *App) ConvertMd2RevealJs(
	inFile string,
	outFile string,
) error {
	logger.Printf("inFile: %s, outFile: %s\n", inFile, outFile)
	if outFile == "" {
		outFile = strings.TrimSuffix(inFile, filepath.Ext(inFile)) + ".pdf"
	}
	args := []string{"-s", inFile, "-t", "revealjs", "-o", outFile}
	config, err := a.LoadConfig()
	if err != nil {
		err = errors.Wrap(err, "")
		return err
	}
	cmd := exec.Command(config.PandocPath, args...)

	err = CheckCmdError(cmd)

	if err != nil {
		err = errors.Wrap(err, "")
		return err
	}
	return nil
}

func (a *App) ConvertDocx2Md(
	inFile string,
	outFile string,
) error {
	logger.Printf("inFile: %s, outFile: %s\n", inFile, outFile)
	if outFile == "" {
		outFile = strings.TrimSuffix(inFile, filepath.Ext(inFile)) + ".md"
	}
	args := []string{"-s", inFile, "-o", outFile}
	config, err := a.LoadConfig()
	if err != nil {
		err = errors.Wrap(err, "")
		return err
	}
	cmd := exec.Command(config.PandocPath, args...)

	err = CheckCmdError(cmd)

	if err != nil {
		err = errors.Wrap(err, "")
		return err
	}
	return nil
}

func (a *App) ConvertHtml2Md(
	inFile string,
	outFile string,
) error {
	logger.Printf("inFile: %s, outFile: %s\n", inFile, outFile)
	if outFile == "" {
		outFile = strings.TrimSuffix(inFile, filepath.Ext(inFile)) + ".md"
	}
	args := []string{"-s", inFile, "-o", outFile}
	config, err := a.LoadConfig()
	if err != nil {
		err = errors.Wrap(err, "")
		return err
	}
	cmd := exec.Command(config.PandocPath, args...)

	err = CheckCmdError(cmd)

	if err != nil {
		err = errors.Wrap(err, "")
		return err
	}
	return nil
}

func (a *App) ConvertTex2Md(
	inFile string,
	outFile string,
) error {
	logger.Printf("inFile: %s, outFile: %s\n", inFile, outFile)
	if outFile == "" {
		outFile = strings.TrimSuffix(inFile, filepath.Ext(inFile)) + ".md"
	}
	args := []string{"-s", inFile, "-o", outFile}
	config, err := a.LoadConfig()
	if err != nil {
		err = errors.Wrap(err, "")
		return err
	}
	cmd := exec.Command(config.PandocPath, args...)

	err = CheckCmdError(cmd)

	if err != nil {
		err = errors.Wrap(err, "")
		return err
	}
	return nil
}

func (a *App) MakeDualLayerPDF(
	inFile string,
	outFile string,
	dpi int,
	pages string,
	lang string,
) error {
	logger.Printf("inFile: %s, outFile: %s, dpi: %d, pages: %s, lang: %s\n", inFile, outFile, dpi, pages, lang)
	args := []string{"dual", "--dpi", fmt.Sprintf("%d", dpi), "--lang", lang}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}
