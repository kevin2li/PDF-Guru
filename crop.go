package main

import "fmt"

func (a *App) CropPDFByBBOX(inFile string, outFile string, bbox []float32, unit string, keepSize bool, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, bbox: %v, unit: %s, keepSize: %v, pages: %s\n", inFile, outFile, bbox, unit, keepSize, pages)
	args := []string{"crop", "--method", "bbox"}
	args = append(args, "--bbox")
	for _, v := range bbox {
		args = append(args, fmt.Sprintf("%f", v))
	}
	if unit != "" {
		args = append(args, "--unit", unit)
	}
	if keepSize {
		args = append(args, "--keep_size")
	}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) CropPDFByMargin(inFile string, outFile string, margin []float32, unit string, keepSize bool, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, margin: %v, unit: %s, keepSize: %v, pages: %s\n", inFile, outFile, margin, unit, keepSize, pages)
	args := []string{"crop", "--method", "margin"}
	args = append(args, "--margin")
	for _, v := range margin {
		args = append(args, fmt.Sprintf("%f", v))
	}
	if unit != "" {
		args = append(args, "--unit", unit)
	}
	if keepSize {
		args = append(args, "--keep_size")
	}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}
