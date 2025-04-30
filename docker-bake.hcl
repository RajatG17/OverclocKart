group "default" {
  targets = ["catalog-service","order-service","api-gateway","auth-service"]
}

target "catalog-service" {
  context = "./catalog-service"
  dockerfile = "Dockerfile"
}

target "order-service" {
  context = "./order-service"
  dockerfile = "Dockerfile"
}

target "api-gateway" {
  context = "./api-gateway"
  dockerfile = "Dockerfile"
}

target "auth-service" {
  context = "./auth-service"
  dockerfile = "Dockerfile"
}