#pragma once

#include <DecentApi/DecentAppApp/DecentApp.h>

namespace Decent
{
	namespace Ias
	{
		class Connector;
	}

	namespace DhtClient
	{
		class ConnectionPool;

		class DhtClientApp : public RaSgx::DecentApp
		{
		public:

			DhtClientApp(const std::string& enclavePath, const std::string& tokenPath, const std::string& wListKey, Net::ConnectionBase& serverConn);

			DhtClientApp(const fs::path& enclavePath, const fs::path& tokenPath, const std::string& wListKey, Net::ConnectionBase& serverConn);

			DhtClientApp(const std::string& enclavePath, const std::string& tokenPath,
				const size_t numTWorker, const size_t numUWorker, const size_t retryFallback, const size_t retrySleep,
				const std::string& wListKey, Net::ConnectionBase& serverConn);

			DhtClientApp(const fs::path& enclavePath, const fs::path& tokenPath,
				const size_t numTWorker, const size_t numUWorker, const size_t retryFallback, const size_t retrySleep,
				const std::string& wListKey, Net::ConnectionBase& serverConn);

			virtual ~DhtClientApp();

			void Init(int64_t maxOpPerTicket);

			virtual void Insert(std::shared_ptr<ConnectionPool> cntPool, const std::string& key, const std::string& val);

			virtual void Update(std::shared_ptr<ConnectionPool> cntPool, const std::string& key, const std::string& val);

			virtual std::string Read(std::shared_ptr<ConnectionPool> cntPool, const std::string& key);

			virtual void Delete(std::shared_ptr<ConnectionPool> cntPool, const std::string& key);

			virtual bool ProcessSmartMessage(const std::string& category, Net::ConnectionBase& connection, Net::ConnectionBase*& freeHeldCnt) override;

		private:
			std::unique_ptr<Ias::Connector> m_ias;
		};
	}
}

