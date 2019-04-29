#pragma once

#include <memory>

namespace Decent
{
	namespace Net
	{
		class ConnectionBase;
	}

	namespace DhtClient
	{
		std::unique_ptr<Net::ConnectionBase> GetConnection2DhtNode(uint64_t& outAddr);
		std::unique_ptr<Net::ConnectionBase> GetConnection2DhtStore(const uint64_t addr);
	}
}
