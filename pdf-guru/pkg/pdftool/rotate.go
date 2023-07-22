package backend

import "fmt"

func RotatePDF(inFile string, outFile string, rotation int, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, rotation: %d, pages: %s\n", inFile, outFile, rotation, pages)
	args := []string{"rotate"}
	if rotation != 0 {
		args = append(args, "--angle", fmt.Sprintf("%d", rotation))
	}
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
