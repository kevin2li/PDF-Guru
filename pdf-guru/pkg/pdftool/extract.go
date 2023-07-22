package backend

func ExtractTextFromPDF(inFile string, outFile string, pages string) error {
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
	return cmdRunner(args, "pdf")
}

func ExtractImageFromPDF(inFile string, outFile string, pages string) error {
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
	return cmdRunner(args, "pdf")
}

func OCRExtract(inFile string, outFile string, pages string, extractType string) error {
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
	return cmdRunner(args, "python")
}
