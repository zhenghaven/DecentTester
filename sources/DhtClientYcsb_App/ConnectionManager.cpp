#include "ConnectionManager.h"

#include <DecentApi/Common/Common.h>
#include <DecentApi/CommonApp/Net/TCPConnection.h>
#include <DecentApi/CommonApp/Tools/ConfigManager.h>

#include "../DhtClient_Enclave/Dht/AppNames.h"
#include "Dht/Messages.h"

using namespace Decent::DhtClient;
using namespace Decent::Tools;
using namespace Decent::Net;

namespace
{
	static const ConfigManager* gsk_configMgrPtr = nullptr;

	static inline std::unique_ptr<Connection> InternalGetConnection(const ConfigItem& configItem, const SmartMessages& hsMsg)
	{
		try
		{
			std::unique_ptr<Connection> connection = std::make_unique<TCPConnection>(configItem.GetAddr(), configItem.GetPort());

			if (connection)
			{
				connection->SendSmartMsg(hsMsg);
			}
			return std::move(connection);
		}
		catch (const std::exception& e)
		{
			PRINT_W("Failed to establish connection. (Err Msg: %s)", e.what());
			return nullptr;
		}
	}

	static inline std::unique_ptr<Connection> InternalGetConnection(uint64_t addr, const SmartMessages& hsMsg)
	{
		try
		{
			std::unique_ptr<Connection> connection = std::make_unique<TCPConnection>(addr);

			if (connection)
			{
				connection->SendSmartMsg(hsMsg);
			}
			return std::move(connection);
		}
		catch (const std::exception& e)
		{
			PRINT_W("Failed to establish connection. (Err Msg: %s)", e.what());
			return nullptr;
		}
	}
}

void ConnectionManager::SetConfigManager(const ConfigManager & mgrRef)
{
	gsk_configMgrPtr = &mgrRef;
}

std::unique_ptr<Decent::Net::Connection> ConnectionManager::GetConnection2DecentDhtNode(uint64_t& outAddr)
{
	const ConfigItem& dhtItem = gsk_configMgrPtr->GetItem(AppNames::sk_decentDHT);
	outAddr = TCPConnection::CombineIpAndPort(TCPConnection::GetIpAddressFromStr(dhtItem.GetAddr()), dhtItem.GetPort());
	return InternalGetConnection(dhtItem, Decent::Dht::FromApp());
}

std::unique_ptr<Connection> ConnectionManager::GetConnection2DecentDhtStore(uint64_t addr)
{
	return InternalGetConnection(addr, Decent::Dht::FromApp());
}