package backend

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/pkg/errors"
)

func PDFConversion(
	inFileList []string,
	outFile string,
	dpi int,
	isMerge bool,
	sortMethod string,
	sortDirection string,
	srcType string,
	dstType string,
	pages string) error {
	logger.Printf("inFileList: %v, outFile: %s, dpi: %d, isMerge: %v, sortMethod: %s, sortDirection: %s, srcType: %s, dstType: %s, pages: %s\n", inFileList, outFile, dpi, isMerge, sortMethod, sortDirection, srcType, dstType, pages)
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
	if sortMethod != "" {
		args = append(args, "--sort-method", sortMethod)
	}
	if sortDirection != "" {
		args = append(args, "--sort-direction", sortDirection)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFileList...)
	logger.Println(args)
	return cmdRunner(args, "pdf")
}

func ConvertPDF2Docx(
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
	return cmdRunner(args, "python")
}

// Pandoc convert

func PandocConvert(
	inFile string,
	outFile string,
	dstType string,
) error {
	logger.Printf("inFile: %s, outFile: %s, dstType: %s\n", inFile, outFile, dstType)
	if outFile == "" {
		outFile = strings.TrimSuffix(inFile, filepath.Ext(inFile)) + dstType
	}
	args := []string{"-s", "-t", dstType[1:], "-o", outFile, inFile}
	logger.Println(args)
	return cmdRunner(args, "pandoc")
}
