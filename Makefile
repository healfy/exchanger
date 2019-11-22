SERVICE=exchanger
PY_DIR=exchanger

WLT_PROTO_F = proto/wallets.proto
TRX_PROTO_F = proto/transactions.proto
CUR_PROTO_F = proto/currencies.proto

PROTO_PATH=proto/exchanger.proto
PROTOC_INCLUDE = \
	-I=/usr/local/include \
	-I proto/ \
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

proto: wallets-proto trx-proto cur-proto

wallets-proto:
	$(PROTOC) $(PROTOC_INCLUDE) $(WLT_PROTO_F) --grpc_python_out=$(PY_DIR)/rpc --python_out=grpc:$(PY_DIR)/rpc

trx-proto:
	$(PROTOC) $(PROTOC_INCLUDE) $(TRX_PROTO_F) --grpc_python_out=$(PY_DIR)/rpc --python_out=grpc:$(PY_DIR)/rpc

cur-proto:
	$(PROTOC) $(PROTOC_INCLUDE) $(CUR_PROTO_F) --grpc_python_out=$(PY_DIR)/rpc --python_out=grpc:$(PY_DIR)/rpc
