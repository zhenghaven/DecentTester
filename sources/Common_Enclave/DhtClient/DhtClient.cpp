#include "DhtClient.h"

#include <DecentApi/Common/make_unique.h>
#include <DecentApi/Common/MbedTls/BigNumber.h>

#include <DecentApi/Common/Net/TlsCommLayer.h>
#include <DecentApi/Common/Net/ConnectionBase.h>

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
	static char gsk_ack[] = "ACK";

}

uint64_t DhtClient::GetSuccessorAddress(const std::array<uint8_t, sk_hashSizeByte>& key, void* cntPoolPtr, States& states)
{
	using namespace Decent::Dht::EncFunc::App;

	//PRINT_I("Finding Successor of %s.", ConstBigNumber(key).Get().ToBigEndianHexStr().c_str());

	CntPair cntPair = states.GetConnectionMgr().GetAny(cntPoolPtr, states);
	SecureCommLayer& comm = cntPair.GetCommLayer();

	comm.SendStruct(k_findSuccessor);

	comm.SendRaw(key.data(), key.size());

	//std::array<uint8_t, 32> resId;
	//comm.ReceiveRaw(resId.data(), resId.size());

	uint64_t addr = 0;
	comm.ReceiveStruct(addr);

	return addr;
}

void DhtClient::GetData(const uint64_t addr, void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key, std::vector<uint8_t>& outData)
{
	using namespace Decent::Dht::EncFunc::App;

	CntPair cntPair = states.GetConnectionMgr().GetNew(cntPoolPtr, addr, states);
	SecureCommLayer& comm = cntPair.GetCommLayer();

	comm.SendStruct(k_getData);

	comm.SendRaw(key.data(), key.size());

	comm.ReceiveMsg(outData);

}

void DhtClient::SetData(const uint64_t addr, void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key, const std::vector<uint8_t>& data)
{
	using namespace Decent::Dht::EncFunc::App;

	CntPair cntPair = states.GetConnectionMgr().GetNew(cntPoolPtr, addr, states);
	SecureCommLayer& comm = cntPair.GetCommLayer();

	comm.SendStruct(k_setData);

	comm.SendRaw(key.data(), key.size());
	comm.SendMsg(data);

	comm.ReceiveStruct(gsk_ack);
}

void DhtClient::GetData(const uint64_t addr, void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key, std::string & outData)
{
	using namespace Decent::Dht::EncFunc::App;

	CntPair cntPair = states.GetConnectionMgr().GetNew(cntPoolPtr, addr, states);
	SecureCommLayer& comm = cntPair.GetCommLayer();

	comm.SendStruct(k_getData);

	comm.SendRaw(key.data(), key.size());

	comm.ReceiveMsg(outData);

}

void DhtClient::SetData(const uint64_t addr, void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key, const std::string & data)
{
	using namespace Decent::Dht::EncFunc::App;

	CntPair cntPair = states.GetConnectionMgr().GetNew(cntPoolPtr, addr, states);
	SecureCommLayer& comm = cntPair.GetCommLayer();

	comm.SendStruct(k_setData);

	comm.SendRaw(key.data(), key.size());
	comm.SendMsg(data);

	comm.ReceiveStruct(gsk_ack);

}

void DhtClient::DelData(const uint64_t addr, void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key)
{
	using namespace Decent::Dht::EncFunc::App;

	CntPair cntPair = states.GetConnectionMgr().GetNew(cntPoolPtr, addr, states);
	SecureCommLayer& comm = cntPair.GetCommLayer();

	comm.SendStruct(k_delData);

	comm.SendRaw(key.data(), key.size());

	comm.ReceiveStruct(gsk_ack);

}
