package backend

import "fmt"

func MakeDualLayerPDF(
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
	return cmdRunner(args, "pdf")
}
