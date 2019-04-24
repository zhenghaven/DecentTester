#include "DhtClient.h"

#include <DecentApi/Common/Common.h>
#include <DecentApi/Common/MbedTls/BigNumber.h>

#include <DecentApi/Common/Net/TlsCommLayer.h>
#include <DecentApi/Common/Ra/TlsConfigWithName.h>
#include <DecentApi/CommonEnclave/Net/EnclaveNetConnector.h>
#include <DecentApi/DecentAppEnclave/AppStatesSingleton.h>

#include "AppNames.h"
#include "FuncNums.h"
#include "DhtConnection.h"

using namespace Decent;
using namespace Decent::Ra;
using namespace Decent::Net;
using namespace Decent::Dht;

using namespace Decent::MbedTlsObj;

namespace
{
	static AppStates& gs_state = GetAppStateSingleton();

	static char gsk_ack[] = "ACK";

	std::shared_ptr<TlsConfigWithName> GetTlsCfg2Dht()
	{
		static std::shared_ptr<TlsConfigWithName> tlsCfg = std::make_shared<TlsConfigWithName>(gs_state, TlsConfigWithName::Mode::ClientHasCert, AppNames::sk_decentDHT);
		return tlsCfg;
	}
}

uint64_t Dht::GetSuccessorAddress(const std::array<uint8_t, sk_hashSizeByte>& key)
{
	using namespace Decent::Dht::EncFunc::App;

	PRINT_I("Finding Successor of %s.", ConstBigNumber(key).Get().ToBigEndianHexStr().c_str());

	std::unique_ptr<EnclaveNetConnector> cnt = GetConnection2DhtNode();
	TlsCommLayer tls(cnt->Get(), GetTlsCfg2Dht(), true);

	tls.SendStruct(k_findSuccessor);

	tls.SendRaw(key.data(), key.size());

	std::array<uint8_t, 32> resId;
	uint64_t addr = 0;

	tls.ReceiveRaw(resId.data(), resId.size());
	tls.ReceiveStruct(addr);

	return addr;
}

void Dht::GetData(const uint64_t addr, const std::array<uint8_t, sk_hashSizeByte>& key, std::vector<uint8_t>& outData)
{
	using namespace Decent::Dht::EncFunc::App;

	std::unique_ptr<EnclaveNetConnector> cnt = GetConnection2DhtStore(addr);
	TlsCommLayer tls(cnt->Get(), GetTlsCfg2Dht(), true);

	tls.SendStruct(k_getData);

	tls.SendRaw(key.data(), key.size());

	tls.ReceiveMsg(outData);
}

void Dht::SetData(const uint64_t addr, const std::array<uint8_t, sk_hashSizeByte>& key, const std::vector<uint8_t>& data)
{
	using namespace Decent::Dht::EncFunc::App;

	std::unique_ptr<EnclaveNetConnector> cnt = GetConnection2DhtStore(addr);
	TlsCommLayer tls(cnt->Get(), GetTlsCfg2Dht(), true);

	tls.SendStruct(k_setData);

	tls.SendRaw(key.data(), key.size());
	tls.SendMsg(data);

	tls.ReceiveStruct(gsk_ack);
}

void Dht::GetData(const uint64_t addr, const std::array<uint8_t, sk_hashSizeByte>& key, std::string & outData)
{
	using namespace Decent::Dht::EncFunc::App;

	std::unique_ptr<EnclaveNetConnector> cnt = GetConnection2DhtStore(addr);
	TlsCommLayer tls(cnt->Get(), GetTlsCfg2Dht(), true);

	tls.SendStruct(k_getData);

	tls.SendRaw(key.data(), key.size());

	tls.ReceiveMsg(outData);
}

void Dht::SetData(const uint64_t addr, const std::array<uint8_t, sk_hashSizeByte>& key, const std::string & data)
{
	using namespace Decent::Dht::EncFunc::App;

	std::unique_ptr<EnclaveNetConnector> cnt = GetConnection2DhtStore(addr);
	TlsCommLayer tls(cnt->Get(), GetTlsCfg2Dht(), true);

	tls.SendStruct(k_setData);

	tls.SendRaw(key.data(), key.size());
	tls.SendMsg(data);

	tls.ReceiveStruct(gsk_ack);
}

void Dht::DelData(const uint64_t addr, const std::array<uint8_t, sk_hashSizeByte>& key)
{
	using namespace Decent::Dht::EncFunc::App;

	std::unique_ptr<EnclaveNetConnector> cnt = GetConnection2DhtStore(addr);
	TlsCommLayer tls(cnt->Get(), GetTlsCfg2Dht(), true);

	tls.SendStruct(k_delData);

	tls.SendRaw(key.data(), key.size());

	tls.ReceiveStruct(gsk_ack);
}
