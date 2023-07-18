package main

import (
	"os"
	"path/filepath"

	"github.com/pdfcpu/pdfcpu/pkg/api"
	"github.com/pdfcpu/pdfcpu/pkg/pdfcpu/model"
	"github.com/pkg/errors"
)

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
