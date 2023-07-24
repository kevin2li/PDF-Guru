package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

type AnkiResponse struct {
	Result []string `json:"result"`
	Error  any      `json:"error"`
}

func (a *App) invoke(address, action string, params map[string]string) ([]string, error) {
	var data map[string]interface{}
	if params == nil {
		data = map[string]interface{}{
			"action":  action,
			"version": 6,
		}
	} else {
		data = map[string]interface{}{
			"action":  action,
			"version": 6,
			"params":  params,
		}
	}
	bytesData, err := json.Marshal(data)
	if err != nil {
		return nil, err
	}
	resp, err := http.Post(address, "application/json", bytes.NewBuffer(bytesData))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("anki Connect Error: %d", resp.StatusCode)
	}
	var result AnkiResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}
	if result.Error != nil {
		return nil, fmt.Errorf("%v", result.Error)
	}
	return result.Result, nil
}

func (a *App) GetDeckNames(address string) ([]string, error) {
	res, err := a.invoke(address, "deckNames", nil)
	if err != nil {
		return nil, err
	}
	return res, nil
}

func (a *App) GetModelNames(address string) ([]string, error) {
	res, err := a.invoke(address, "modelNames", nil)
	if err != nil {
		return nil, err
	}
	return res, nil
}

func (a *App) GetModelFieldNames(address string, model string) ([]string, error) {
	params := map[string]string{"modelName": model}
	res, err := a.invoke(address, "modelFieldNames", params)
	if err != nil {
		return nil, err
	}
	return res, nil
}

func (a *App) GetTags(address string) ([]string, error) {
	res, err := a.invoke(address, "getTags", nil)
	if err != nil {
		return nil, err
	}
	return res, nil
}

func (a *App) CreateCardByRectAnnots(
	inFile string,
	outFile string,
	address string,
	parentDeck string,
	mode []string,
	createSubDeck bool,
	level int,
	q_mask_color string,
	a_mask_color string,
	dpi int,
	tags []string,
	imageMode bool,
	maskTypes []string,
	pages string) error {
	logger.Printf("inFile: %s, outFile: %s, address: %s, parentDeck: %s, mode: %v, createSubDeck: %v, level: %d, q_mask_color: %s, a_mask_color: %s, dpi: %d, tags: %v, pages: %s\n", inFile, outFile, address, parentDeck, mode, createSubDeck, level, q_mask_color, a_mask_color, dpi, tags, pages)
	args := []string{"anki"}
	args = append(args, inFile)
	args = append(args, "--type", "rect_annots")
	args = append(args, "--address", address)
	args = append(args, "--parent-deck", parentDeck)
	args = append(args, "--mode")
	args = append(args, mode...)
	if createSubDeck {
		args = append(args, "--create-sub-deck")
	}
	args = append(args, "--level", fmt.Sprintf("%d", level))
	args = append(args, "--q-mask-color", q_mask_color)
	args = append(args, "--a-mask-color", a_mask_color)
	args = append(args, "--dpi", fmt.Sprintf("%d", dpi))
	if len(tags) > 0 {
		args = append(args, "--tags")
		args = append(args, tags...)
	}
	if len(maskTypes) > 0 {
		args = append(args, "--mask-types")
		args = append(args, maskTypes...)
	}
	if imageMode {
		args = append(args, "--image-mode")
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

func (a *App) CreateCardByFontStyle(
	inFile string,
	outFile string,
	matches []string,
	pages string) error {
	logger.Printf("inFile: %s, outFile: %s, matches: %v, pages: %s\n", inFile, outFile, matches, pages)
	args := []string{"anki"}
	args = append(args, "--type", "font_style")
	args = append(args, "--matches")
	args = append(args, matches...)
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

func (a *App) CreateQACard(
	inFile string,
	outFile string,
	address string,
	parentDeck string,
	modelName string,
	fieldMapping string,
	createSubDeck bool,
	level int,
	dpi int,
	tags []string,
	pages string) error {
	logger.Printf("inFile: %s, outFile: %s, address: %s, parentDeck: %s, modelName: %s, fieldMapping: %s, createSubDeck: %v, level: %d, dpi: %d, tags: %v, pages: %s\n", inFile, outFile, address, parentDeck, modelName, fieldMapping, createSubDeck, level, dpi, tags, pages)
	args := []string{"anki"}
	args = append(args, inFile)
	args = append(args, "--type", "qa_card")
	args = append(args, "--address", address)
	args = append(args, "--parent-deck", parentDeck)
	args = append(args, "--model", modelName)
	if createSubDeck {
		args = append(args, "--create-sub-deck")
	}
	args = append(args, "--level", fmt.Sprintf("%d", level))
	args = append(args, "--dpi", fmt.Sprintf("%d", dpi))
	if fieldMapping != ""{
		args = append(args, "--field-mapping", fieldMapping)
	}
	if len(tags) > 0 {
		args = append(args, "--tags")
		args = append(args, tags...)
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
