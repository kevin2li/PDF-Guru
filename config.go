package main

import (
	"encoding/json"
	"os"
	"path/filepath"
	"runtime"

	"github.com/pkg/errors"
)

type MyConfig struct {
	PdfPath       string `json:"pdf_path"`
	PythonPath    string `json:"python_path"`
	TesseractPath string `json:"tesseract_path"`
	PandocPath    string `json:"pandoc_path"`
	HashcatPath   string `json:"hashcat_path"`
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
	configPath := filepath.Join(logdir, "config.json")
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
	configPath := filepath.Join(logdir, "config.json")
	if _, err := os.Stat(configPath); os.IsNotExist(err) {
		a.ResetConfig()
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
	pdfPath, err := a.GetPdfPath()
	if err != nil {
		err = errors.Wrap(err, "")
		return config, err
	}
	if config.PdfPath != pdfPath {
		config.PdfPath = pdfPath
		err = a.SaveConfig(pdfPath, config.PythonPath, config.TesseractPath, config.PandocPath, config.HashcatPath)
		if err != nil {
			err = errors.Wrap(err, "")
			return config, err
		}
	}
	return config, nil
}

func (a *App) GetPdfPath() (string, error) {
	path, err := os.Executable()
	if err != nil {
		err = errors.Wrap(err, "")
		logger.Errorln("Error:", err)
		return "", err
	}
	pdfPath := filepath.Join(filepath.Dir(path), "pdf.exe")
	if runtime.GOOS == "darwin" {
		pdfPath = filepath.Join(filepath.Dir(filepath.Dir(filepath.Dir(filepath.Dir(path)))), "pdf")
	} else if runtime.GOOS == "linux" {
		pdfPath = filepath.Join(filepath.Dir(path), "pdf")
	}
	return pdfPath, nil
}

func (a *App) ResetConfig() error {
	pdfPath, err := a.GetPdfPath()
	if err != nil {
		err = errors.Wrap(err, "")
		return err
	}
	err = a.SaveConfig(pdfPath, "", "", "", "")
	if err != nil {
		err = errors.Wrap(err, "")
		return err
	}
	return nil
}
