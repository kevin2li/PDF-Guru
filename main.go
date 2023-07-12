package main

import (
	"embed"
	"io"
	"os"

	"github.com/pkg/errors"
	"github.com/sirupsen/logrus"
	"github.com/wailsapp/wails/v2"
	"github.com/wailsapp/wails/v2/pkg/options"
	"github.com/wailsapp/wails/v2/pkg/options/assetserver"
)

//go:embed all:frontend/dist
var assets embed.FS

var (
	log    *logrus.Logger
	logger *logrus.Entry
)

func main() {
	// init logger
	log = logrus.New()
	file, err := os.OpenFile("access.log", os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
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

	// Create an instance of the app structure
	app := NewApp()

	// Create application with options
	err = wails.Run(&options.App{
		Title:  "PDF Guru",
		Width:  1280,
		Height: 880,
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
		err = errors.Wrap(err, "")
		println("Error:", err.Error())
	}

	logger.Info("exiting pdf-guru")
}
