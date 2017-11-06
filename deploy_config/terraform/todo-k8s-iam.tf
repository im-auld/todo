module "todo-k8s-iam" {
  source       = "git::ssh://git@bitbucket.org/offerup/terraform///modules/k8s-service"

  service_name = "todo-k8s"
  environment  = "${terraform.env}"
}

output "aws_iam_role.todo-k8s_service.name" {
  value = "${module.todo-k8s-iam.aws_iam_role.service.name}"
}

output "aws_iam_role.todo-k8s_service.arn" {
  value = "${module.todo-k8s-iam.aws_iam_role.service.arn}"
}

output "aws_iam_role.todo-k8s_lambda.name" {
  value = "${module.todo-k8s-iam.aws_iam_role.service_lambda.name}"
}

output "aws_iam_role.todo-k8s_lambda.arn" {
  value = "${module.todo-k8s-iam.aws_iam_role.service_lambda.arn}"
}

output "aws_iam_instance_profile.todo-k8s.name" {
  value = "${module.todo-k8s-iam.aws_iam_instance_profile.service.name}"
}

output "aws_iam_instance_profile.todo-k8s.arn" {
  value = "${module.todo-k8s-iam.aws_iam_instance_profile.service.arn}"
}
