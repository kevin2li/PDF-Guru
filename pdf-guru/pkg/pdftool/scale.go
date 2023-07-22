package backend

import "fmt"

func ScalePDFByScale(inFile string, outFile string, scale float32, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, scale: %f, pages: %s\n", inFile, outFile, scale, pages)
	args := []string{"resize", "--method", "scale"}
	args = append(args, "--scale", fmt.Sprintf("%f", scale))
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

func ScalePDFByDim(inFile string, outFile string, width float32, height float32, unit string, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, width: %f, height: %f, unit: %s, pages: %s\n", inFile, outFile, width, height, unit, pages)
	args := []string{"resize", "--method", "dim"}
	args = append(args, "--width", fmt.Sprintf("%f", width))
	args = append(args, "--height", fmt.Sprintf("%f", height))
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if unit != "" {
		args = append(args, "--unit", unit)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)
	return cmdRunner(args, "pdf")
}

func ScalePDFByPaperSize(inFile string, outFile string, paperSize string, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, paperSize: %s, pages: %s\n", inFile, outFile, paperSize, pages)
	args := []string{"resize", "--method", "paper_size"}
	if paperSize != "" {
		args = append(args, "--paper_size", paperSize)
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
