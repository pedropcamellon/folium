output "resource_group_name" {
  value = module.resource_group.name
}

output "static_web_app_name" {
  value = module.static_web_app.name
}

output "demo_url" {
  value = "https://${module.static_web_app.default_host_name}"
}
