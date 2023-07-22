package backend

import "os"

func EncryptPDF(inFile string, outFile string, upw string, opw string, perm []string) error {
	logger.Printf("inFile: %s, outFile: %s, upw: %s, opw: %s, perm: %v\n", inFile, outFile, upw, opw, perm)
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		logger.Errorln(err)
		return err
	}
	args := []string{"encrypt"}
	if len(perm) > 0 {
		args = append(args, "--perm")
		args = append(args, perm...)
	}
	if upw != "" {
		args = append(args, "--user_password", upw)
	}
	if opw != "" {
		args = append(args, "--owner_password", opw)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)

	return cmdRunner(args, "pdf")
}

func DecryptPDF(inFile string, outFile string, passwd string) error {
	logger.Printf("inFile: %s, outFile: %s, passwd: %s\n", inFile, outFile, passwd)
	if _, err := os.Stat(inFile); os.IsNotExist(err) {
		logger.Errorln(err)
		return err
	}
	args := []string{"decrypt"}
	if passwd != "" {
		args = append(args, "--password", passwd)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)
	return cmdRunner(args, "pdf")
}

func ChangePasswordPDF(inFile string, outFile string, oldUpw string, upw string, oldOpw string, opw string) error {
	logger.Printf("inFile: %s, outFile: %s, oldUpw: %s, upw: %s, oldOpw: %s, opw: %s\n", inFile, outFile, oldUpw, upw, oldOpw, opw)
	args := []string{"change_password"}
	if oldUpw != "" {
		args = append(args, "--old_user_password", oldUpw)
	}
	if upw != "" {
		args = append(args, "--user_password", upw)
	}
	if oldOpw != "" {
		args = append(args, "--old_owner_password", oldOpw)
	}
	if opw != "" {
		args = append(args, "--owner_password", opw)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)
	return cmdRunner(args, "pdf")
}
