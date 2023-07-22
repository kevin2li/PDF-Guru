package backend

import "fmt"

func CutPDFByGrid(inFile string, outFile string, row int, col int, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, row: %d, col: %d, pages: %s\n", inFile, outFile, row, col, pages)
	args := []string{"cut", "--method", "grid"}
	args = append(args, "--nrow", fmt.Sprintf("%d", row))
	args = append(args, "--ncol", fmt.Sprintf("%d", col))
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

func CutPDFByBreakpoints(inFile string, outFile string, HBreakpoints []float32, VBreakpoints []float32, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, HBreakpoints: %v, VBreakpoints: %v, pages: %s\n", inFile, outFile, HBreakpoints, VBreakpoints, pages)
	args := []string{"cut", "--method", "breakpoints"}
	args = append(args, inFile)
	if len(HBreakpoints) > 0 {
		args = append(args, "--h_breakpoints")
		for _, v := range HBreakpoints {
			args = append(args, fmt.Sprintf("%f", v))
		}
	}
	if len(VBreakpoints) > 0 {
		args = append(args, "--v_breakpoints")
		for _, v := range VBreakpoints {
			args = append(args, fmt.Sprintf("%f", v))
		}
	}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	logger.Println(args)
	return cmdRunner(args, "pdf")
}

func CombinePDFByGrid(inFile string, outFile string, row int, col int, pages string, paperSize string, orientation string) error {
	logger.Printf("inFile: %s, outFile: %s, row: %d, col: %d, pages: %s, paperSize: %s, orientation: %s\n", inFile, outFile, row, col, pages, paperSize, orientation)
	args := []string{"combine"}
	args = append(args, "--nrow", fmt.Sprintf("%d", row))
	args = append(args, "--ncol", fmt.Sprintf("%d", col))
	if paperSize != "" {
		args = append(args, "--paper_size", paperSize)
	}
	if orientation != "" {
		args = append(args, "--orientation", orientation)
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
