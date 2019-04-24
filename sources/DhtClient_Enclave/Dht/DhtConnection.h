#pragma once

#include <memory>

namespace Decent
{
	namespace Net
	{
		class EnclaveNetConnector;
	}

	namespace Dht
	{
		std::unique_ptr<Net::EnclaveNetConnector> GetConnection2DhtNode();
		std::unique_ptr<Net::EnclaveNetConnector> GetConnection2DhtStore(const uint64_t addr);
	}
}
