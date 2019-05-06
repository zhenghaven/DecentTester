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
		namespace UntrustedConnectionPool
		{
			std::pair<std::unique_ptr<Net::ConnectionBase>, uint64_t> GetAnyDhtNode(void* cntPoolPtr);

			std::unique_ptr<Net::ConnectionBase> GetDhtNode(void* cntPoolPtr, uint64_t addr);
		}
	}
}
