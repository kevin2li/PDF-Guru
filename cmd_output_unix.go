//go:build darwin || linux

package main

import (
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/pkg/errors"
)

type CmdOutput struct {
	Status  string `json:"status"`
	Message string `json:"message"`
}

func GetCmdStatusAndMessage(cmd *exec.Cmd, cmdType string) error {
	defer func() {
		if err := recover(); err != nil {
			logger.Fatalln(err)
		}
	}()

	out, err := cmd.CombinedOutput()
	if err != nil {
		// err = errors.Wrap(err, "get cmd output error! \n args: "+strings.Join(cmd.Args, " ")+"\n stderr: "+string(err.(*exec.ExitError).Stderr))
		err = errors.Wrap(err, "命令执行失败!"+string(out))
		logger.Errorln("Error:", err)

		return err
	}
	logger.Println(string(out))

	if cmdType == "pdf" {
		ret_path := filepath.Join(logdir, "cmd_output.json")
		var ret CmdOutput
		data, err := os.ReadFile(ret_path)
		if err != nil {
			err = errors.Wrap(err, "read cmd output file error")
			return err
		}
		err = json.Unmarshal(data, &ret)
		if err != nil {
			err = errors.Wrap(err, "json umarshal error")
			return err
		}

		if ret.Status != "success" {
			logger.Errorf("Error: %v\n", ret.Message)
			return errors.New(ret.Message)
		}
	}

	return nil
}

func (a *App) cmdRunner(args []string, cmdType string) error {
	config, err := a.LoadConfig()
	if err != nil {
		err = errors.Wrap(err, "")
		return err
	}
	var cmd *exec.Cmd
	if cmdType == "pdf" {
		cmd = exec.Command(config.PdfPath, args...)
	} else if cmdType == "python" {
		err = a.CheckFileExists(config.PythonPath)
		if err != nil {
			return err
		}
		cmd = exec.Command(config.PythonPath, args...)
	} else if cmdType == "pandoc" {
		path := config.PandocPath
		err = a.CheckFileExists(config.PandocPath)
		if err != nil {
			pandoc_path, err := exec.LookPath("pandoc.exe")
			if err != nil {
				err = errors.Wrap(err, "pandoc not found!")
				return err
			}
			path = pandoc_path
		}
		cmd = exec.Command(path, args...)
	} else if cmdType == "tesseract" {
		path := config.TesseractPath
		err = a.CheckFileExists(config.TesseractPath)
		if err != nil {
			tesseract_path, err := exec.LookPath("tesseract.exe")
			if err != nil {
				err = errors.Wrap(err, "tesseract not found!")
				return err
			}
			path = tesseract_path
		}
		cmd = exec.Command(path, args...)
	} else if cmdType == "hashcat" {
		err = a.CheckFileExists(config.HashcatPath)
		if err != nil {
			err = errors.Wrap(err, "hashcat not found!")
			return err
		}
		cmd = exec.Command(config.HashcatPath, args...)
	} else {
		err = errors.Wrap(err, "unsupport cmd type!")
		return err
	}
	err = GetCmdStatusAndMessage(cmd, cmdType)
	if err != nil {
		err = errors.Wrap(err, "")
		return err
	}
	return nil
}
