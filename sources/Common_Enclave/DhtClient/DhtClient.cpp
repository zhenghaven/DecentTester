#include "DhtClient.h"

#include <atomic>

#include <DecentApi/Common/make_unique.h>
#include <DecentApi/Common/MbedTls/BigNumber.h>

#include <DecentApi/Common/Net/TlsCommLayer.h>
#include <DecentApi/Common/Net/ConnectionBase.h>
#include <DecentApi/Common/Net/RpcWriter.h>
#include <DecentApi/Common/Net/RpcParser.h>

#include "AccessCtrl/EntityList.h"
#include "AccessCtrl/FullPolicy.h"

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

void DhtClient::AppInsertData(const uint64_t addr, void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key, const Dht::AccessCtrl::FullPolicy& accPolicy, const std::vector<uint8_t>& data)
{
	using namespace Decent::Dht::EncFunc;
	using namespace Decent::Dht::EncFunc::App;

	size_t accPolicyBinSize = accPolicy.GetSerializedSize();

	CntPair cntPair = states.GetConnectionMgr().GetNew(cntPoolPtr, addr, states);
	SecureCommLayer& comm = cntPair.GetCommLayer();

	RpcWriter rpc(RpcWriter::CalcSizePrim<NumType>() +
		RpcWriter::CalcSizePrim<uint8_t[sk_hashSizeByte]>() +
		RpcWriter::CalcSizeBin(accPolicyBinSize) +
		RpcWriter::CalcSizeBin(data.size()), 4);

	auto funcNum = rpc.AddPrimitiveArg<NumType>();
	auto queryKey = rpc.AddPrimitiveArg<uint8_t[sk_hashSizeByte]>();
	auto accPolicyBin = rpc.AddBinaryArg(accPolicyBinSize);
	auto dataToSend = rpc.AddBinaryArg(data.size());

	funcNum = k_insertData;
	std::copy(key.begin(), key.end(), std::begin(queryKey.Get()));
	accPolicy.Serialize(accPolicyBin.begin(), accPolicyBin.end());
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

uint64_t DhtClient::GetAttrListAddress(const std::string & listName, void * cntPoolPtr, States & states)
{
	using namespace Decent::Dht::EncFunc::User;

	CntPair cntPair = states.GetConnectionMgr().GetAny(cntPoolPtr, states);
	SecureCommLayer& comm = cntPair.GetCommLayer();

	RpcWriter rpc(RpcWriter::CalcSizePrim<NumType>() +
		RpcWriter::CalcSizeStr(listName.size()), 2);

	auto funcNum = rpc.AddPrimitiveArg<NumType>();
	auto listNameToSend = rpc.AddStringArg(listName.size());

	funcNum = k_findAtListSuc;
	listNameToSend.Fill(listName);

	comm.SendRpc(rpc);

	uint64_t addr = 0;
	comm.ReceiveStruct(addr);

	return addr;
}

void DhtClient::UserInsertAttrList(const uint64_t addr, void * cntPoolPtr, States & states, const std::string & listName, const Dht::AccessCtrl::EntityList & list)
{
	using namespace Decent::Dht::EncFunc;
	using namespace Decent::Dht::EncFunc::User;

	CntPair cntPair = states.GetConnectionMgr().GetAny(cntPoolPtr, states);
	SecureCommLayer& comm = cntPair.GetCommLayer();

	size_t listBinSize = list.GetSerializedSize();

	RpcWriter rpc(RpcWriter::CalcSizePrim<NumType>() +
		RpcWriter::CalcSizeStr(listName.size()) +
		RpcWriter::CalcSizeBin(listBinSize), 3);

	auto funcNum = rpc.AddPrimitiveArg<NumType>();
	auto listNameToSend = rpc.AddStringArg(listName.size());
	auto listBin = rpc.AddBinaryArg(listBinSize);

	funcNum = k_insertAttList;
	listNameToSend.Fill(listName);
	list.Serialize(listBin.begin());

	comm.SendRpc(rpc);

	RpcParser rpcReturned(comm.ReceiveBinary());

	const auto& retVal = rpcReturned.GetPrimitiveArg<FileOpRet::NumType>();

	CheckDhtStoreRpcError(retVal);
}

std::vector<uint8_t> Decent::DhtClient::UserReadData(const uint64_t addr, void * cntPoolPtr, States & states, const std::array<uint8_t, sk_hashSizeByte>& key)
{
	using namespace Decent::Dht::EncFunc;
	using namespace Decent::Dht::EncFunc::User;

	CntPair cntPair = states.GetConnectionMgr().GetAny(cntPoolPtr, states);
	SecureCommLayer& comm = cntPair.GetCommLayer();

	std::shared_ptr<CachedAttributeList> cachedAttrList = std::atomic_load(&(states.GetAttributeCache()));

	const size_t listBinSize = cachedAttrList ? cachedAttrList->m_list.size() : 0;
	const size_t certPemSize = cachedAttrList ? cachedAttrList->m_certPem.size() : 0;

	RpcWriter rpc(RpcWriter::CalcSizePrim<NumType>() +
		RpcWriter::CalcSizePrim<uint8_t[sk_hashSizeByte]>() +
		RpcWriter::CalcSizePrim<uint8_t>() +
		RpcWriter::CalcSizeBin(listBinSize) +
		RpcWriter::CalcSizePrim<general_secp256r1_signature_t>() +
		RpcWriter::CalcSizeStr(certPemSize), 6);

	auto funcNum = rpc.AddPrimitiveArg<NumType>();
	auto Key2Send = rpc.AddPrimitiveArg<uint8_t[sk_hashSizeByte]>();
	auto hasCache = rpc.AddPrimitiveArg<uint8_t>();
	auto listBin = rpc.AddBinaryArg(listBinSize);
	auto cacheSign = rpc.AddPrimitiveArg<general_secp256r1_signature_t>();
	auto certPem = rpc.AddStringArg(certPemSize);

	funcNum = k_readData;
	std::copy(key.begin(), key.end(), std::begin(Key2Send.Get()));

	if (cachedAttrList)
	{
		hasCache = 1; //true
		std::copy(cachedAttrList->m_list.begin(), cachedAttrList->m_list.end(), listBin.begin());
		cacheSign = cachedAttrList->m_sign;
		certPem.Fill(cachedAttrList->m_certPem);
	}
	else
	{
		hasCache = 0; //false
	}

	comm.SendRpc(rpc);

	RpcParser rpcReturned(comm.ReceiveBinary());

	const auto& retVal = rpcReturned.GetPrimitiveArg<FileOpRet::NumType>();
	auto retData = rpcReturned.GetBinaryArg();
	const auto& retHasCache = rpcReturned.GetPrimitiveArg<uint8_t>();

	CheckDhtStoreRpcError(retVal);

	if (retHasCache)
	{
		std::shared_ptr<CachedAttributeList> updatedCache = std::make_shared<CachedAttributeList>();

		auto retCacheList = rpcReturned.GetBinaryArg();
		updatedCache->m_sign = rpcReturned.GetPrimitiveArg<general_secp256r1_signature_t>();
		updatedCache->m_certPem = rpcReturned.GetStringArg();

		updatedCache->m_list = std::vector<uint8_t>(retCacheList.first, retCacheList.second);

		std::atomic_store(&(states.GetAttributeCache()), updatedCache);
	}

	return std::vector<uint8_t>(retData.first, retData.second);
}
