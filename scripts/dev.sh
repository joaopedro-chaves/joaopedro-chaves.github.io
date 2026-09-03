#!/bin/bash

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m"
SERVICE_NAME="joaopedro-chaves.io"

print_message() {
    echo -e "${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}$1${NC}"
}

print_error() {
    echo -e "${RED}$1${NC}"
}

check_requirements() {
    print_message "Verificando pré-requisitos..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker não encontrado. Por favor, instale o Docker (https://docs.docker.com/get-docker/) e tente novamente."
        exit 1
    fi

    if ! command -v docker compose &> /dev/null; then
        print_error "Docker Compose não encontrado. Por favor, instale o Docker Compose (https://docs.docker.com/compose/install/) e tente novamente."
        exit 1
    fi

    if ! command -v go &> /dev/null; then
        print_error "Go não encontrado. Por favor, instale o Go (https://go.dev/dl/) e tente novamente."
        exit 1
    fi

    if ! command -v hugo &> /dev/null; then
        print_error "Hugo não encontrado. Por favor, instale o Hugo (https://gohugo.io/installation/) e tente novamente."
        exit 1
    fi

    # Aviso se Docker está instalado mas sem permissão de socket
    if ! docker info &> /dev/null; then
        print_warning "Docker instalado, mas sem permissão de acesso ao socket."
        print_warning "Para usar o Docker, execute: sudo usermod -aG docker \$USER && newgrp docker"
    fi
}

start_dev() {
    read -p "Iniciar com o Docker ou Hugo? (D[docker]/H[hugo]): " answer_starter
    if [[ $answer_starter =~ ^[Dd]$ ]]; then
        print_message "Iniciando com o Docker..."
        docker compose up --build -d
        print_message "Servidor em: http://localhost:8000"
    else
        print_message "Iniciando com o Hugo..."
        cd ..
        hugo mod tidy && hugo server --bind 0.0.0.0 -p 8000 --disableFastRender --buildDrafts
        print_message "Servidor em: http://localhost:8000"
    fi
}

stop_dev() {
    read -p "Parar Docker ou Hugo? (D[docker]/H[hugo]): " answer_stop
    if [[ $answer_stop =~ ^[Dd]$ ]]; then
        print_message "Parando ambiente Docker..."
        docker compose down
    else
        print_message "Parando servidor Hugo..."
        pkill -f "hugo server" && print_message "Hugo parado com sucesso." || print_warning "Nenhum processo Hugo encontrado."
    fi
}

reload_dev() {
    read -p "Reiniciar Docker ou Hugo? (D[docker]/H[hugo]): " answer_reload
    if [[ $answer_reload =~ ^[Dd]$ ]]; then
        print_message "Reiniciando ambiente Docker..."
        docker compose down
        docker compose up --build -d
        print_message "Ambiente Docker reiniciado em: http://localhost:8000"
    else
        print_message "Reiniciando servidor Hugo..."
        pkill -f "hugo server" || true
        hugo mod tidy && hugo server --bind 0.0.0.0 -p 8000 --disableFastRender --buildDrafts
    fi
}

logs() {
    read -p "Logs do Docker ou Hugo? (D[docker]/H[hugo]): " answer_logs
    if [[ $answer_logs =~ ^[Dd]$ ]]; then
        print_message "Logs do Docker..."
        docker compose logs -f
    else
        print_message "Hugo escreve os logs diretamente no terminal ao iniciar com './dev.sh start'."
    fi
}

new_post() {
    print_message "Criando novo post..."

    post_dir="content/blog"
    date_full=$(date +"%Y-%m-%d")
    year=$(date +"%Y")

    read -p "Título do post: " title
    slug=$(echo "$title" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
    
    post_dir_year="$post_dir/$year"

    if [ ! -d "$post_dir_year" ]; then
        mkdir -p "$post_dir_year"
        print_message "Pasta do ano $year criada com sucesso!"
    fi

    post_path="$post_dir_year/$date_full-$slug.md"
    
    read -p "Descrição do post: " description
    read -p "Tags do post: " tags

    cat << EOF > $post_path
---
title: "$title"
description: "$description"
date: $date_full
tags: $tags
---

Conteúdo do post aqui...

EOF

    print_message "Post criado com sucesso! "
}

reload_index() {
    print_message "Recarregando index..."
    python scripts/generate_index.py
    print_message "Index recarregado"
}

show_help() {
    echo "Uso: $0 {start|stop|reload|logs|new-post|help}"
    echo ""
    echo "Opções:"
    echo "  start    Inicia o ambiente de desenvolvimento."
    echo "  stop     Para o ambiente de desenvolvimento."
    echo "  reload   Reinicia o ambiente de desenvolvimento."
    echo "  logs     Exibe os logs do ambiente de desenvolvimento."
    echo "  new-post Cria um novo post."
    echo "  help     Exibe esta mensagem."
}

main() {
    check_requirements

    case "${1}" in
        start)
            start_dev
            ;;
        stop)
            stop_dev
            ;;
        reload)
            reload_dev
            ;;
        new-post)
            new_post
            ;;
        help)
            show_help
            ;;
        logs)
            logs
            ;;
        reload_index)
            reload_index
            ;;
        *)  
            print_warning "Comando invalido"
            show_help
            exit 1
            ;;
    esac
}

main "$@"