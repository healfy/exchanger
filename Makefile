SERVICE=exchanger
PY_DIR=exchanger

WLT_PROTO = py-wallets/proto
WLT_PROTO_F = py-wallets/proto/wallets.proto

TRX_PROTO = transactions/proto
TRX_PROTO_F = transactions/proto/transactions.proto

PROTO_PATH=proto/exchanger.proto
PROTOC_INCLUDE = \
	-I=/usr/local/include \
	-I proto/ \
	-I $(WLT_PROTO) \
	-I $(TRX_PROTO) \
	-I${GOPATH}/src/github.com/grpc-ecosystem/grpc-gateway/third_party/googleapis \
	-I${GOPATH}/src/github.com/grpc-ecosystem/grpc-gateway

PROTOC = python3 -m grpc.tools.protoc

.PHONY: proto
proto: OUT_DIR=$(PY_DIR)/rpc

proto: $(PROTO_PATH)
	mkdir -p $(OUT_DIR)
	$(PROTOC) $(PROTOC_INCLUDE) \
		--grpc_python_out=$(OUT_DIR) \
		--python_grpc_out=$(OUT_DIR) \
		--python_out=plugins=grpc:$(OUT_DIR) $(PROTO_PATH)

wallets-proto:
	$(PROTOC) $(PROTOC_INCLUDE) $(WLT_PROTO_F) --grpc_python_out=$(PY_DIR)/rpc --python_out=grpc:$(PY_DIR)/rpc

trx-proto:
	$(PROTOC) $(PROTOC_INCLUDE) $(TRX_PROTO_F) --grpc_python_out=$(PY_DIR)/rpc --python_out=grpc:$(PY_DIR)/rpc
