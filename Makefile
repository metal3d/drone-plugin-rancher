IMAGE=metal3d/drone-plugin-rancher
MAJOR=v1
MINOR=$(MAJOR).0
REL=$(MINOR).0

build:
	docker build -t $(IMAGE):$(REL) .

push:
	docker tag $(IMAGE):$(REL) $(IMAGE):$(MINOR)
	docker tag $(IMAGE):$(REL) $(IMAGE):$(MAJOR)
	docker tag $(IMAGE):$(REL) $(IMAGE):latest
	docker push $(IMAGE):$(REL)
	docker push $(IMAGE):$(MINOR)
	docker push $(IMAGE):$(MAJOR)
	docker push $(IMAGE):latest


