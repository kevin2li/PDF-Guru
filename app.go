package main

import (
	"context"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"

	"github.com/pdfcpu/pdfcpu/pkg/api"
	"github.com/pdfcpu/pdfcpu/pkg/pdfcpu"
	"github.com/pdfcpu/pdfcpu/pkg/pdfcpu/model"
	"github.com/pdfcpu/pdfcpu/pkg/pdfcpu/types"
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

// Greet returns a greeting for the given name
func (a *App) Greet(name string) string {
	return fmt.Sprintf("Hello %s, It's show time!", name)
}

func (a *App) Test() string {
	formatted := time.Now().Format("2006-01-02 15:04:05")
	return fmt.Sprintf("当前时间:  %s", formatted)
}

func (a *App) SplitPDF(inFile string, mode string, span int, outDir string) error {
	fmt.Println("inFile: ", inFile)
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		fmt.Println(err)
		return err
	}
	if _, err := os.Stat(outDir); os.IsNotExist(err) {
		err = os.MkdirAll(outDir, os.ModePerm)
		if err != nil {
			return err
		}
	}
	conf := model.NewDefaultConfiguration()
	if mode == "span" {
		err := api.SplitFile(inFile, outDir, span, conf)
		if err != nil {
			return err
		}
	} else if mode == "bookmark" {
		fmt.Println("bookmark")
	}
	return nil
}

func (a *App) RotatePDF(inFile string, outFile string, rotation int, pagesStr string) error {
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		fmt.Println(err)
		return err
	}

	pages, err := api.ParsePageSelection(pagesStr)
	if err != nil {
		fmt.Fprintf(os.Stderr, "problem with flag selectedPages: %v\n", err)
		return err
	}
	conf := model.NewDefaultConfiguration()
	err = api.RotateFile(inFile, outFile, rotation, pages, conf)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) ScalePDF(inFile string, outFile string, description string, pagesStr string) error {
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		fmt.Println(err)
		return err
	}
	pages, err := api.ParsePageSelection(pagesStr)
	if err != nil {
		return err
	}
	resizeConf, err := pdfcpu.ParseResizeConfig(description, types.POINTS)
	if err != nil {
		return err
	}
	conf := model.NewDefaultConfiguration()
	err = api.ResizeFile(inFile, outFile, pages, resizeConf, conf)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) ReorderPDF(inFile string, outFile string, pagesStr string) error {
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		fmt.Println(err)
		return err
	}
	pages, err := api.ParsePageSelection(pagesStr)
	if err != nil {
		return err
	}

	conf := model.NewDefaultConfiguration()
	err = api.CollectFile(inFile, outFile, pages, conf)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) CompressPDF(inFile string, outFile string) error {
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		fmt.Println(err)
		return err
	}
	conf := model.NewDefaultConfiguration()
	err := api.OptimizeFile(inFile, outFile, conf)
	if err != nil {
		return err
	}
	return nil
}

func (a *App) MergePDF(inFiles []string, outFile string, mode string, sort bool) error {
	if len(inFiles) == 0 {
		return errors.New("no input files")
	}
	filesIn := []string{}
	for _, inFile := range inFiles {
		if strings.Contains(inFile, "*") {
			matches, err := filepath.Glob(inFile)
			if err != nil {
				fmt.Fprintf(os.Stderr, "%s", err)
				os.Exit(1)
			}
			filesIn = append(filesIn, matches...)
			continue
		}
		if _, err := os.Stat(inFile); os.IsNotExist(err) {
			return err
		}
		filesIn = append(filesIn, inFile)

	}
	conf := model.NewDefaultConfiguration()
	if mode == "create" {
		err := api.MergeCreateFile(filesIn, outFile, conf)
		if err != nil {
			return err
		}
	} else if mode == "append" {
		err := api.MergeAppendFile(filesIn, outFile, conf)
		if err != nil {
			return err
		}
	}
	return nil
}

func (a *App) WatermarkPDF(inFile string, outFile string, wmFile string, mode string, pagesStr string) error {
	return nil
}

func (a *App) EncryptPDF(inFile string, outFile string, algorithm string, userPW string, ownerPW string, key int, perm string) error {
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		fmt.Println(err)
		return err
	}
	if algorithm == "AES" {
		conf := model.NewAESConfiguration(userPW, ownerPW, key)
		err := api.EncryptFile(inFile, outFile, conf)
		if err != nil {
			return err
		}
		if perm == "all" {
			conf.Permissions = model.PermissionsAll
		} else if perm == "none" {
			conf.Permissions = model.PermissionsNone
			
		}
		err = api.SetPermissionsFile(outFile, "", conf)
		if err != nil {
			return err
		}
	} else if algorithm == "RC4" {
		conf := model.NewRC4Configuration(userPW, ownerPW, key)
		err := api.EncryptFile(inFile, outFile, conf)
		if err != nil {
			return err
		}
		if perm == "all" {
			conf.Permissions = model.PermissionsAll
		} else if perm == "none" {
			conf.Permissions = model.PermissionsNone
		}
		err = api.SetPermissionsFile(outFile, "", conf)
		if err != nil {
			return err
		}
	}

	return nil
}

func (a *App) DecryptPDF(inFile string, outFile string, userPW string, ownerPW string) error {
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		fmt.Println(err)
		return err
	}
	var lastErr error
	flag := false
	// try AES
	for keyLen := range [3]int{256, 128, 40} {
		conf := model.NewAESConfiguration(userPW, ownerPW, keyLen)
		err := api.DecryptFile(inFile, outFile, conf)
		if err != nil {
			fmt.Println(err)
			lastErr = err
			continue
		}
		flag = true
		return nil
	}

	// try RC4
	for keyLen := range [2]int{128, 40} {
		conf := model.NewRC4Configuration(userPW, ownerPW, keyLen)
		err := api.DecryptFile(inFile, outFile, conf)
		if err != nil {
			fmt.Println(err)
			lastErr = err
			continue
		}
		flag = true
		return nil
	}
	if !flag {
		return lastErr
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
