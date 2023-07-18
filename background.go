package main

import "fmt"

func (a *App) AddPDFBackgroundByImage(inFile string, imgFile string, outFile string, opacity float32, angle float32, x_offset float32, y_offset float32, scale float32, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, imgFile: %s, opacity: %f, angle: %f, x_offset: %f, y_offset: %f, pages: %s\n", inFile, outFile, imgFile, opacity, angle, x_offset, y_offset, pages)
	args := []string{"bg", "--type", "image"}
	if imgFile != "" {
		args = append(args, "--img-path", imgFile)
	}
	args = append(args, "--opacity", fmt.Sprintf("%f", opacity))
	args = append(args, "--angle", fmt.Sprintf("%f", angle))
	args = append(args, "--x-offset", fmt.Sprintf("%f", x_offset))
	args = append(args, "--y-offset", fmt.Sprintf("%f", y_offset))
	args = append(args, "--scale", fmt.Sprintf("%f", scale))
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

func (a *App) AddPDFBackgroundByColor(inFile string, outFile string, color string, opacity float32, angle float32, x_offset float32, y_offset float32, pages string) error {
	logger.Printf("inFile: %s, outFile: %s, color: %s, opacity: %f, angle: %f, x_offset: %f, y_offset: %f, pages: %s\n", inFile, outFile, color, opacity, angle, x_offset, y_offset, pages)
	args := []string{"bg", "--type", "color"}
	if color != "" {
		args = append(args, "--color", color)
	}
	args = append(args, "--opacity", fmt.Sprintf("%f", opacity))
	args = append(args, "--angle", fmt.Sprintf("%f", angle))
	args = append(args, "--x-offset", fmt.Sprintf("%f", x_offset))
	args = append(args, "--y-offset", fmt.Sprintf("%f", y_offset))
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
