package backend

import "fmt"

func SplitPDFByChunk(inFile string, chunkSize int, outDir string) error {
	logger.Printf("inFile: %s, chunkSize: %d, outDir: %s\n", inFile, chunkSize, outDir)
	args := []string{"split", "--mode", "chunk"}
	args = append(args, "--chunk_size")
	args = append(args, fmt.Sprintf("%d", chunkSize))
	if outDir != "" {
		args = append(args, "--output", outDir)
	}
	args = append(args, inFile)
	logger.Println(args)

	return cmdRunner(args, "pdf")
}

func SplitPDFByBookmark(inFile string, tocLevel string, outDir string) error {
	logger.Printf("inFile: %s, outDir: %s\n", inFile, outDir)
	args := []string{"split", "--mode", "toc"}
	if tocLevel != "" {
		args = append(args, "--toc-level", tocLevel)
	}
	if outDir != "" {
		args = append(args, "--output", outDir)
	}
	args = append(args, inFile)
	logger.Println(args)

	return cmdRunner(args, "pdf")
}

func SplitPDFByPage(inFile string, pages string, outDir string) error {
	logger.Printf("inFile: %s, pages: %s, outDir: %s\n", inFile, pages, outDir)
	args := []string{"split", "--mode", "page"}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outDir != "" {
		args = append(args, "--output", outDir)
	}
	args = append(args, inFile)
	logger.Println(args)

	return cmdRunner(args, "pdf")
}
