package main

func (a *App) AnnotParser(inFile string, outFile string, method string, annotTypes []string, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, method: %s, annotTypes: %v, pages: %s\n", inFile, outFile, method, annotTypes, pages)
	args := []string{"annot"}
	args = append(args, inFile)
	args = append(args, "--method", method)
	if len(annotTypes) > 0 {
		args = append(args, "--annot-types")
		args = append(args, annotTypes...)
	}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}

	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}
