package main

import (
	"github.com/pkg/errors"
	wails_runtime "github.com/wailsapp/wails/v2/pkg/runtime"
)

func (a *App) SelectFile() string {
	d, err := wails_runtime.OpenFileDialog(a.ctx, wails_runtime.OpenDialogOptions{})
	if err != nil {
		logger.Errorln(err)
		return ""
	}
	logger.Debugf("%v\n", d)
	return d
}

func (a *App) SelectMultipleFiles() []string {
	d, err := wails_runtime.OpenMultipleFilesDialog(a.ctx, wails_runtime.OpenDialogOptions{})
	if err != nil {
		logger.Errorln(err)
		return nil
	}
	logger.Debugf("%v\n", d)
	return d
}

func (a *App) SelectDir() string {
	d, err := wails_runtime.OpenDirectoryDialog(a.ctx, wails_runtime.OpenDialogOptions{})
	if err != nil {
		logger.Errorln(err)
		return ""
	}
	logger.Debugf("%v\n", d)
	return d
}

func (a *App) SaveFile() string {
	d, err := wails_runtime.SaveFileDialog(a.ctx, wails_runtime.SaveDialogOptions{})
	if err != nil {
		logger.Errorln(err)
		return ""
	}
	logger.Debugf("%v\n", d)
	return d
}

func (a *App) OpenUrl(url string) {
	wails_runtime.BrowserOpenURL(a.ctx, url)
}

func (a *App) GetClipboard() string {
	text, err := wails_runtime.ClipboardGetText(a.ctx)
	if err != nil {
		logger.Errorln(err)
		return ""
	}
	return text
}

func (a *App) SetClipboard(content string) error {
	err := wails_runtime.ClipboardSetText(a.ctx, content)
	if err != nil {
		logger.Errorln(err)
		err = errors.Wrap(err, "set clipboard error")
		return err
	}
	return nil
}
