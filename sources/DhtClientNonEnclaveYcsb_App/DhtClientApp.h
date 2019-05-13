#pragma once

#include <memory>
#include <string>

namespace Decent
{
	namespace Ra
	{
		class AppCertContainer;
		class KeyContainer;

		namespace WhiteList
		{
			class DecentServer;
		}
	}

	namespace DhtClient
	{
		class ConnectionPool;
		class ConnectionManager;
		class States;

		class DhtClientApp
		{
		public:
			DhtClientApp();

			virtual ~DhtClientApp();

			void Init();

			virtual void Insert(std::shared_ptr<ConnectionPool> cntPool, const std::string& key, const std::string& val);

			virtual std::string Read(std::shared_ptr<ConnectionPool> cntPool, const std::string& key);

			virtual void Delete(std::shared_ptr<ConnectionPool> cntPool, const std::string& key);

		private:
			std::unique_ptr<Ra::AppCertContainer> m_certContainer;
			std::unique_ptr<Ra::KeyContainer> m_keyContainer;
			std::unique_ptr<Ra::WhiteList::DecentServer> m_serverWl;

			std::unique_ptr<ConnectionManager> m_connectionMgr;

			std::unique_ptr<DhtClient::States> m_states;
		};
	}
}

