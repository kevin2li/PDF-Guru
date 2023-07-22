package backend

func ReorderPDF(inFile string, outFile string, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, pages: %s\n", inFile, outFile, pages)
	args := []string{"reorder"}
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
