#pragma once

#include <DecentApi/DecentAppApp/DecentApp.h>

namespace Decent
{
	namespace DhtClient
	{
		class ConnectionPool;

		class DhtClientApp : public Decent::RaSgx::DecentApp
		{
		public:
			using DecentApp::DecentApp;

			virtual ~DhtClientApp();

			void Init();

			virtual void Insert(std::shared_ptr<ConnectionPool> cntPool, const std::string& key, const std::string& val);

			virtual void Update(std::shared_ptr<ConnectionPool> cntPool, const std::string& key, const std::string& val);

			virtual std::string Read(std::shared_ptr<ConnectionPool> cntPool, const std::string& key);

			virtual void Delete(std::shared_ptr<ConnectionPool> cntPool, const std::string& key);

			virtual bool ProcessSmartMessage(const std::string& category, Net::ConnectionBase& connection, Net::ConnectionBase*& freeHeldCnt) override;

		private:
		};
	}
}

