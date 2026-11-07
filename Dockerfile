# Generated for Glama / Smithery / Automated Container Checks
FROM node:20-alpine

WORKDIR /app

COPY package.json README.md LICENSE ./
COPY bin ./bin
COPY golden_sandbox_50.json ./golden_sandbox_50.json

RUN npm link

ENTRYPOINT ["veriscope-mcp"]
