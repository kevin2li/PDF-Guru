package main

import (
	"embed"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"runtime"

	"github.com/pkg/errors"
	"github.com/sirupsen/logrus"
	"github.com/wailsapp/wails/v2"
	"github.com/wailsapp/wails/v2/pkg/options"
	"github.com/wailsapp/wails/v2/pkg/options/assetserver"
)

//go:embed all:frontend/dist
var assets embed.FS

// go:embed all:thirdparty/ocr.py
// go:embed all:thirdparty/convert.py
// go:embed all:thirdparty/dist/pdf.exe
// var thirdpartyAsset embed.FS

var (
	log    *logrus.Logger
	logger *logrus.Entry
	logdir string
	// tmpDir string
)

func main() {
	defer func() {
		if err := recover(); err != nil {
			fmt.Println("Error:", err)
		}
	}()
	// init logger
	log = logrus.New()
	if runtime.GOOS == "windows" {
		logdir = filepath.Join(os.Getenv("USERPROFILE"), ".pdf_guru")
	} else {
		logdir = filepath.Join(os.Getenv("HOME"), ".pdf_guru")
	}
	err := os.MkdirAll(logdir, 0755)
	if err != nil {
		err = errors.Wrap(err, "failed to create log directory")
		log.Fatal(err)
	}
	logpath := filepath.Join(logdir, "access.log")
	file, err := os.OpenFile(logpath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
	if err != nil {
		err = errors.Wrap(err, "failed to create log file")
		log.Fatal(err)
	}
	defer file.Close()

	log.SetOutput(io.MultiWriter(os.Stdout, file))
	log.SetLevel(logrus.DebugLevel)
	log.SetReportCaller(true)
	log.SetFormatter(&logrus.TextFormatter{
		TimestampFormat: "2006-01-02 15:04:05",
		FullTimestamp:   true,
		DisableColors:   true,
	})
	logger = log.WithFields(logrus.Fields{
		"service": "pdf-guru",
	})
	logger.Info("starting pdf-guru")

	// init tmp directory
	// tmpDir = filepath.Join(os.TempDir(), "pdf-guru")
	// logger.Info("tmpDir: ", tmpDir)
	// err = os.MkdirAll(tmpDir, 0755)
	// if err != nil {
	// 	err = errors.Wrap(err, "failed to create tmp directory")
	// 	logger.Fatal(err)
	// }

	// filenames := []string{"ocr.py", "convert.py", "pdf.exe"}
	// for _, filename := range filenames {
	// 	content, err := thirdpartyAsset.ReadFile("thirdparty/" + filename)
	// 	if err != nil {
	// 		err = errors.Wrap(err, "failed to read "+filename)
	// 		logger.Fatal(err)
	// 	}
	// 	err = os.WriteFile(filepath.Join(tmpDir, filename), content, 0755)
	// 	if err != nil {
	// 		err = errors.Wrap(err, "failed to write "+filename)
	// 		logger.Fatal(err)
	// 	}
	// 	defer os.Remove(filepath.Join(tmpDir, filename))
	// }

	// Create an instance of the app structure
	app := NewApp()

	// Create application with options
	err = wails.Run(&options.App{
		Title:     "PDF Guru",
		Width:     1280,
		Height:    700,
		MinWidth:  1000,
		MinHeight: 600,
		AssetServer: &assetserver.Options{
			Assets: assets,
		},
		BackgroundColour: &options.RGBA{R: 27, G: 38, B: 54, A: 1},
		OnStartup:        app.startup,
		Bind: []interface{}{
			app,
		},
	})

	if err != nil {
		err = errors.Wrap(err, "run wails app failed")
		fmt.Println("Error:", err.Error())
	}

	logger.Info("exiting pdf-guru")
}
