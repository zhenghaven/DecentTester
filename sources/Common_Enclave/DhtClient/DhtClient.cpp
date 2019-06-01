#include "DhtClient.h"

#include <DecentApi/Common/make_unique.h>
#include <DecentApi/Common/MbedTls/BigNumber.h>

#include <DecentApi/Common/Net/TlsCommLayer.h>
#include <DecentApi/Common/Net/ConnectionBase.h>
#include <DecentApi/Common/Net/RpcWriter.h>
#include <DecentApi/Common/Net/RpcParser.h>

#include "AppNames.h"
#include "FuncNums.h"
#include "States.h"
#include "ConnectionManager.h"

using namespace Decent;
using namespace Decent::Net;
using namespace Decent::DhtClient;
using namespace Decent::MbedTlsObj;

namespace
{
	static void CheckDhtStoreRpcError(uint8_t errCode)
	{
		using namespace Decent::Dht::EncFunc::FileOpRet;
		switch (errCode)
		{
		case k_nonExist: throw DataNonExist();
		case k_denied: throw PermissionDenied();
		default:
			break;
		}
	}
}

uint64_t DhtClient::GetSuccessorAddress(const std::array<uint8_t, sk_hashSizeByte>& key, void* cntPoolPtr, States& states)
{
	using namespace Decent::Dht::EncFunc::App;

	//PRINT_I("Finding Successor of %s.", ConstBigNumber(key).Get().ToBigEndianHexStr().c_str());

	CntPair cntPair = states.GetConnectionMgr().GetAny(cntPoolPtr, states);
	SecureCommLayer& comm = cntPair.GetCommLayer();

	RpcWriter rpc(RpcWriter::CalcSizePrim<NumType>() +
		RpcWriter::CalcSizePrim<uint8_t[sk_hashSizeByte]>(), 2);

	auto funcNum = rpc.AddPrimitiveArg<NumType>();
	auto queryKey = rpc.AddPrimitiveArg<uint8_t[sk_hashSizeByte]>();

	funcNum = k_findSuccessor;
	std::copy(key.begin(), key.end(), std::begin(queryKey.Get()));

	comm.SendRpc(rpc);

	uint64_t addr = 0;
	comm.ReceiveStruct(addr);

	return addr;
}

std::vector<uint8_t> DhtClient::AppReadData(const uint64_t addr, void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key)
{
	using namespace Decent::Dht::EncFunc;
	using namespace Decent::Dht::EncFunc::App;

	CntPair cntPair = states.GetConnectionMgr().GetNew(cntPoolPtr, addr, states);
	SecureCommLayer& comm = cntPair.GetCommLayer();

	RpcWriter rpc(RpcWriter::CalcSizePrim<NumType>() +
		RpcWriter::CalcSizePrim<uint8_t[sk_hashSizeByte]>(), 2);

	auto funcNum = rpc.AddPrimitiveArg<NumType>();
	auto queryKey = rpc.AddPrimitiveArg<uint8_t[sk_hashSizeByte]>();

	funcNum = k_readData;
	std::copy(key.begin(), key.end(), std::begin(queryKey.Get()));

	comm.SendRpc(rpc);

	RpcParser rpcReturned(comm.ReceiveBinary());
	
	const auto& retVal = rpcReturned.GetPrimitiveArg<FileOpRet::NumType>();
	auto retData = rpcReturned.GetBinaryArg();

	CheckDhtStoreRpcError(retVal);

	return std::vector<uint8_t>(retData.first, retData.second);
}

void DhtClient::AppInsertData(const uint64_t addr, void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key, const std::vector<uint8_t>& meta, const std::vector<uint8_t>& data)
{
	using namespace Decent::Dht::EncFunc;
	using namespace Decent::Dht::EncFunc::App;

	CntPair cntPair = states.GetConnectionMgr().GetNew(cntPoolPtr, addr, states);
	SecureCommLayer& comm = cntPair.GetCommLayer();

	RpcWriter rpc(RpcWriter::CalcSizePrim<NumType>() +
		RpcWriter::CalcSizePrim<uint8_t[sk_hashSizeByte]>() +
		RpcWriter::CalcSizeBin(meta.size()) +
		RpcWriter::CalcSizeBin(data.size()), 4);

	auto funcNum = rpc.AddPrimitiveArg<NumType>();
	auto queryKey = rpc.AddPrimitiveArg<uint8_t[sk_hashSizeByte]>();
	auto metaToSend = rpc.AddBinaryArg(meta.size());
	auto dataToSend = rpc.AddBinaryArg(data.size());

	funcNum = k_insertData;
	std::copy(key.begin(), key.end(), std::begin(queryKey.Get()));
	std::copy(meta.begin(), meta.end(), metaToSend.begin());
	std::copy(data.begin(), data.end(), dataToSend.begin());

	comm.SendRpc(rpc);

	RpcParser rpcReturned(comm.ReceiveBinary());

	const auto& retVal = rpcReturned.GetPrimitiveArg<FileOpRet::NumType>();

	CheckDhtStoreRpcError(retVal);
}

void DhtClient::AppUpdateData(const uint64_t addr, void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key, const std::vector<uint8_t>& data)
{
	using namespace Decent::Dht::EncFunc;
	using namespace Decent::Dht::EncFunc::App;

	CntPair cntPair = states.GetConnectionMgr().GetNew(cntPoolPtr, addr, states);
	SecureCommLayer& comm = cntPair.GetCommLayer();

	RpcWriter rpc(RpcWriter::CalcSizePrim<NumType>() +
		RpcWriter::CalcSizePrim<uint8_t[sk_hashSizeByte]>() +
		RpcWriter::CalcSizeBin(data.size()), 3);

	auto funcNum = rpc.AddPrimitiveArg<NumType>();
	auto queryKey = rpc.AddPrimitiveArg<uint8_t[sk_hashSizeByte]>();
	auto dataToSend = rpc.AddBinaryArg(data.size());

	funcNum = k_updateData;
	std::copy(key.begin(), key.end(), std::begin(queryKey.Get()));
	std::copy(data.begin(), data.end(), dataToSend.begin());

	comm.SendRpc(rpc);

	RpcParser rpcReturned(comm.ReceiveBinary());

	const auto& retVal = rpcReturned.GetPrimitiveArg<FileOpRet::NumType>();

	CheckDhtStoreRpcError(retVal);
}

void DhtClient::AppDeleteData(const uint64_t addr, void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key)
{
	using namespace Decent::Dht::EncFunc;
	using namespace Decent::Dht::EncFunc::App;

	CntPair cntPair = states.GetConnectionMgr().GetNew(cntPoolPtr, addr, states);
	SecureCommLayer& comm = cntPair.GetCommLayer();

	RpcWriter rpc(RpcWriter::CalcSizePrim<NumType>() +
		RpcWriter::CalcSizePrim<uint8_t[sk_hashSizeByte]>(), 2);

	auto funcNum = rpc.AddPrimitiveArg<NumType>();
	auto queryKey = rpc.AddPrimitiveArg<uint8_t[sk_hashSizeByte]>();

	funcNum = k_delData;
	std::copy(key.begin(), key.end(), std::begin(queryKey.Get()));

	comm.SendRpc(rpc);

	RpcParser rpcReturned(comm.ReceiveBinary());

	const auto& retVal = rpcReturned.GetPrimitiveArg<FileOpRet::NumType>();

	CheckDhtStoreRpcError(retVal);
}
