package main

import (
	"fmt"
	"os"
)

func (a *App) WatermarkPDFByText(inFile string, outFile string, markText string, fontFamily string, fontSize int, fontColor string, angle int, opacity float32, num_lines int, line_spacing float32, word_spacing float32, x_offset float32, y_offset float32, multiple_mode bool, layer string, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, markText: %s, fontFamily: %s, fontSize: %d, fontColor: %s, angle: %d, opacity: %f, num_lines: %d, line_spacing: %f, word_spacing: %f, x_offset: %f, y_offset: %f, multiple_mode: %v, layer: %s\n", inFile, outFile, markText, fontFamily, fontSize, fontColor, angle, opacity, num_lines, line_spacing, word_spacing, x_offset, y_offset, multiple_mode, layer)
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		logger.Errorln(err)
		return err
	}
	args := []string{"watermark", "add"}
	if markText != "" {
		args = append(args, "--mark-text", markText)
	}
	if fontFamily != "" {
		args = append(args, "--font-family", fontFamily)
	}
	if fontColor != "" {
		args = append(args, "--color", fontColor)
	}
	args = append(args, "--font-size", fmt.Sprintf("%d", fontSize))
	args = append(args, "--angle", fmt.Sprintf("%d", angle))
	args = append(args, "--opacity", fmt.Sprintf("%f", opacity))
	args = append(args, "--num-lines", fmt.Sprintf("%d", num_lines))
	args = append(args, "--line-spacing", fmt.Sprintf("%f", line_spacing))
	args = append(args, "--word-spacing", fmt.Sprintf("%f", word_spacing))
	args = append(args, "--x-offset", fmt.Sprintf("%f", x_offset))
	args = append(args, "--y-offset", fmt.Sprintf("%f", y_offset))
	if multiple_mode {
		args = append(args, "--multiple-mode")
	}
	if layer != "" {
		args = append(args, "--layer", layer)
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

func (a *App) WatermarkPDFByImage(inFile string, outFile string, wmPath string, angle int, opacity float32, scale float32, num_lines int, line_spacing float32, word_spacing float32, x_offset float32, y_offset float32, multiple_mode bool, layer string, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, wmPath: %s, angle: %d, opacity: %f, scale: %f, num_lines: %d, line_spacing: %f, word_spacing: %f, x_offset: %f, y_offset: %f, multiple_mode: %v, layer: %s\n", inFile, outFile, wmPath, angle, opacity, scale, num_lines, line_spacing, word_spacing, x_offset, y_offset, multiple_mode, layer)
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		logger.Errorln(err)
		return err
	}
	args := []string{"watermark", "add", "--type", "image"}
	if wmPath != "" {
		args = append(args, "--wm-path", wmPath)
	}
	args = append(args, "--angle", fmt.Sprintf("%d", angle))
	args = append(args, "--opacity", fmt.Sprintf("%f", opacity))
	args = append(args, "--scale", fmt.Sprintf("%f", scale))
	args = append(args, "--num-lines", fmt.Sprintf("%d", num_lines))
	args = append(args, "--line-spacing", fmt.Sprintf("%f", line_spacing))
	args = append(args, "--word-spacing", fmt.Sprintf("%f", word_spacing))
	args = append(args, "--x-offset", fmt.Sprintf("%f", x_offset))
	args = append(args, "--y-offset", fmt.Sprintf("%f", y_offset))
	if multiple_mode {
		args = append(args, "--multiple-mode")
	}
	if layer != "" {
		args = append(args, "--layer", layer)
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

func (a *App) WatermarkPDFByPDF(inFile string, outFile string, wmPath string, layer string, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, wmPath: %s, layer: %s\n", inFile, outFile, wmPath, layer)
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		logger.Errorln(err)
		return err
	}
	args := []string{"watermark", "add", "--type", "pdf"}
	if wmPath != "" {
		args = append(args, "--wm-path", wmPath)
	}
	if layer != "" {
		args = append(args, "--layer", layer)
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

func (a *App) RemoveWatermarkByType(inFile string, outFile string, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, pages: %s\n", inFile, outFile, pages)
	args := []string{"watermark", "remove", "--method", "type"}
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

func (a *App) RemoveWatermarkByIndex(inFile string, outFile string, wmIndex []int, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, wmIndex: %v, pages: %s\n", inFile, outFile, wmIndex, pages)
	args := []string{"watermark", "remove"}
	args = append(args, inFile)
	args = append(args, "--method", "index")
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	args = append(args, "--wm_index")
	for _, v := range wmIndex {
		args = append(args, fmt.Sprintf("%d", v))
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) DetectWatermarkByIndex(inFile string, outFile string, wmIndex int) error {
	logger.Printf("inFile: %s, outFile: %s, wmIndex: %d\n", inFile, outFile, wmIndex)
	args := []string{"watermark", "detect"}
	args = append(args, inFile)
	args = append(args, "--wm_index")
	args = append(args, fmt.Sprintf("%d", wmIndex))
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) MaskPDFByRect(inFile string, outFile string, rect []float32, unit string, color string, opacity float32, angle float32, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, rect: %v, unit: %s, color: %s, opacity: %f, angle: %f, pages: %s\n", inFile, outFile, rect, unit, color, opacity, angle, pages)
	args := []string{"mask", "--type", "rect"}
	args = append(args, "--bbox")
	for _, v := range rect {
		args = append(args, fmt.Sprintf("%f", v))
	}
	if unit != "" {
		args = append(args, "--unit", unit)
	}
	if color != "" {
		args = append(args, "--color", color)
	}
	args = append(args, "--opacity", fmt.Sprintf("%f", opacity))
	args = append(args, "--angle", fmt.Sprintf("%f", angle))
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

func (a *App) MaskPDFByAnnot(inFile string, outFile string, annot_page int, color string, opacity float32, angle float32, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, annot_page: %d, color: %s, opacity: %f, angle: %f, pages: %s\n", inFile, outFile, annot_page, color, opacity, angle, pages)
	args := []string{"mask", "--type", "annot"}
	args = append(args, "--annot-page", fmt.Sprintf("%d", annot_page))
	if color != "" {
		args = append(args, "--color", color)
	}
	args = append(args, "--opacity", fmt.Sprintf("%f", opacity))
	args = append(args, "--angle", fmt.Sprintf("%f", angle))
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
