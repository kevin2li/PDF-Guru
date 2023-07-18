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
