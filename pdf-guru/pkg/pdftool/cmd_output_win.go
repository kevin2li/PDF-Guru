//go:build windows

package backend

import (
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
	"syscall"

	"github.com/pkg/errors"
)

type CmdOutput struct {
	Status  string `json:"status"`
	Message string `json:"message"`
}

type MyConfig struct {
	PdfPath       string `json:"pdf_path"`
	PythonPath    string `json:"python_path"`
	TesseractPath string `json:"tesseract_path"`
	PandocPath    string `json:"pandoc_path"`
	HashcatPath   string `json:"hashcat_path"`
}

func GetCmdStatusAndMessage(cmd *exec.Cmd, cmdType string) error {
	defer func() {
		if err := recover(); err != nil {
			logger.Fatalln(err)
		}
	}()
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}

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

func cmdRunner(args []string, cmdType string) error {
	var config MyConfig
	config_path := "config.json"
	data, err := os.ReadFile(config_path)
	if err != nil {
		err = errors.Wrap(err, "")
		return err
	}
	json.Unmarshal(data, &config)
	if err != nil {
		err = errors.Wrap(err, "")
		return err
	}
	var cmd *exec.Cmd
	if cmdType == "pdf" {
		cmd = exec.Command(config.PdfPath, args...)
	} else if cmdType == "python" {
		cmd = exec.Command(config.PythonPath, args...)
	} else if cmdType == "pandoc" {
		path := config.PandocPath
		cmd = exec.Command(path, args...)
	} else if cmdType == "tesseract" {
		path := config.TesseractPath
		cmd = exec.Command(path, args...)
	} else if cmdType == "hashcat" {
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
