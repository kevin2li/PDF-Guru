package backend

import (
	"fmt"
	"os"
	"path/filepath"
)

func ExtractBookmark(inFile string, outFile string, format string) error {
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
	return cmdRunner(args, "pdf")
}

func WriteBookmarkByFile(inFile string, outFile string, tocFile string, offset int) error {
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
	return cmdRunner(args, "pdf")
}

func WriteBookmarkByGap(inFile string, outFile string, gap int, format string, startNumber int, pages string) error {
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
	return cmdRunner(args, "pdf")
}

func TransformBookmark(inFile string, outFile string, addOffset int, levelDict []string, deleteLevelBelow int, defaultLevel int, isRemoveBlankLines bool) error {
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
	return cmdRunner(args, "pdf")
}

func DetectBookmarkByFont(
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
	return cmdRunner(args, "pdf")
}

func OCR(inFile string, outFile string, pages string, lang string, doubleColumn bool) error {
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
	return cmdRunner(args, "python")
}

func OCRPDFBookmark(inFile string, outFile string, pages string, lang string, doubleColumn bool) error {
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
	return cmdRunner(args, "python")
}
