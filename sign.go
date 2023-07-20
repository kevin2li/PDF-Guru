package main

func (a *App) SignImage(inFile string, outFile string) error {
	logger.Printf("inFile: %s, outFile: %s\n", inFile, outFile)
	args := []string{"sign"}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}
