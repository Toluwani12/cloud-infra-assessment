terraform {
  backend "s3" {
    bucket       = "cloud-assessment-state-151065283508-eu-west-1"
    key          = "learning/terraform.tfstate"
    region       = "eu-west-1"
    encrypt      = true
    use_lockfile = true
  }
}