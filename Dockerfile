ARG IMAGE_LOCATION=opticrd/odoo
ARG ODOO_VERSION=14.0
FROM ${IMAGE_LOCATION}:${ODOO_VERSION}

ARG ODOO_VERSION
ENV ODOO_EXTRA_ADDONS /mnt/extra-addons
ENV ODOO_VERSION ${ODOO_VERSION}

USER root
RUN sudo mkdir -p ${ODOO_EXTRA_ADDONS}

RUN git clone --depth 1 --branch ${ODOO_VERSION} --single-branch https://github.com/indexa-git/odoo-cloud-platform.git ${ODOO_EXTRA_ADDONS}/camptocamp/odoo-cloud-platform \
    && git clone --depth 1 --branch ${ODOO_VERSION} --single-branch https://github.com/OCA/partner-contact.git ${ODOO_EXTRA_ADDONS}/oca/partner-contact \
    && git clone --depth 1 --branch ${ODOO_VERSION} --single-branch https://github.com/OCA/sale-workflow.git ${ODOO_EXTRA_ADDONS}/oca/sale-workflow \
    && git clone --depth 1 --branch ${ODOO_VERSION} --single-branch https://github.com/OCA/purchase-workflow.git ${ODOO_EXTRA_ADDONS}/oca/purchase-workflow \
    && git clone --depth 1 --branch ${ODOO_VERSION} --single-branch https://github.com/OCA/stock-logistics-workflow.git ${ODOO_EXTRA_ADDONS}/oca/stock-logistics-workflow \
    && git clone --depth 1 --branch ${ODOO_VERSION} --single-branch https://github.com/OCA/stock-logistics-warehouse.git ${ODOO_EXTRA_ADDONS}/oca/stock-logistics-warehouse \
    && git clone --depth 1 --branch ${ODOO_VERSION} --single-branch https://github.com/OCA/wms.git ${ODOO_EXTRA_ADDONS}/oca/wms \
    && git clone --depth 1 --branch ${ODOO_VERSION} --single-branch https://github.com/OCA/account-payment.git ${ODOO_EXTRA_ADDONS}/oca/account-payment \
    && git clone --depth 1 --branch ${ODOO_VERSION} --single-branch https://github.com/OCA/account-analytic.git ${ODOO_EXTRA_ADDONS}/oca/account-analytic \
    && git clone --depth 1 --branch ${ODOO_VERSION} --single-branch https://github.com/OCA/operating-unit.git ${ODOO_EXTRA_ADDONS}/oca/operating-unit \
    && git clone --depth 1 --branch ${ODOO_VERSION} --single-branch https://github.com/OCA/product-attribute.git ${ODOO_EXTRA_ADDONS}/oca/product-attribute \
    && git clone --depth 1 --branch ${ODOO_VERSION} --single-branch https://github.com/OCA/web.git ${ODOO_EXTRA_ADDONS}/oca/web \
    && git clone --depth 1 --branch ${ODOO_VERSION} --single-branch https://github.com/OCA/server-tools.git ${ODOO_EXTRA_ADDONS}/oca/server-tools \
    && git clone --depth 1 --branch ${ODOO_VERSION} --single-branch https://github.com/OCA/server-ux.git ${ODOO_EXTRA_ADDONS}/oca/server-ux \
    && git clone --depth 1 --branch ${ODOO_VERSION} --single-branch https://github.com/OCA/connector.git ${ODOO_EXTRA_ADDONS}/oca/connector \
    && git clone --depth 1 --branch ${ODOO_VERSION} --single-branch https://github.com/OCA/rest-framework.git ${ODOO_EXTRA_ADDONS}/oca/rest-framework \
    && git clone --depth 1 --branch ${ODOO_VERSION} --single-branch https://github.com/indexa-git/l10n-dominicana.git ${ODOO_EXTRA_ADDONS}/indexa/l10n-dominicana \
    && git clone --depth 1 --branch ${ODOO_VERSION} --single-branch https://github.com/indexa-git/external-service-addons.git ${ODOO_EXTRA_ADDONS}/indexa/external-service-addons

COPY . ${ODOO_EXTRA_ADDONS}

RUN apt-get -qq update && apt-get -qq install -y --no-install-recommends build-essential \
    && find ${ODOO_EXTRA_ADDONS} -name 'requirements.txt' -exec pip3 --no-cache-dir install -r {} \; \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

RUN sudo chown -R 1000:1000 ${ODOO_EXTRA_ADDONS}

RUN if [ "${ODOO_VERSION}" = "14.0" ]; then \
    cd /opt/odoo && \
    curl https://patch-diff.githubusercontent.com/raw/odoo/odoo/pull/64772.patch | git apply - && \
    curl https://patch-diff.githubusercontent.com/raw/odoo/odoo/pull/69352.patch | git apply - && \
    git status; \
    fi

USER 1000