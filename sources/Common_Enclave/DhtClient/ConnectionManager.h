#pragma once

#include <DecentApi/Common/Tools/SharedCachingQueue.h>
#include <DecentApi/Common/Net/SecureConnectionPoolBase.h>

namespace Decent
{
	namespace MbedTlsObj
	{
		class Session;
	}

	namespace DhtClient
	{
		class States;

		class ConnectionManager
		{
		public:
			ConnectionManager(size_t cacheSize);

			virtual ~ConnectionManager();

			virtual Net::CntPair GetNew(void* cntPoolPtr, const uint64_t& addr, States& state);

			virtual Net::CntPair GetAny(void* cntPoolPtr, States& state);

		private:
			Tools::SharedCachingQueue<uint64_t, MbedTlsObj::Session> m_sessionCache;
		};
	}
}
