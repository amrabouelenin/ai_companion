#!/bin/bash

# Script to manage and test LLM models
# Usage: ./model-manager.sh [command]

MODEL_LIST_FILE="/home/amro/local_llm/models.txt"

function list_models() {
    echo "Listing all available models..."
    docker exec -it ollama ollama list > $MODEL_LIST_FILE
    cat $MODEL_LIST_FILE
}

function benchmark_model() {
    local model="$1"
    if [ -z "$model" ]; then
        echo "Please specify a model name (e.g. tinyllama, llama2, or fast-tinyllama)"
        return 1
    fi
    
    echo "Benchmarking model: $model"
    echo "Testing response speed with a standard prompt..."
    time docker exec -it ollama ollama run $model "Write a short paragraph about artificial intelligence. Keep it brief."
    
    echo -e "\nTesting memory usage..."
    docker stats ollama --no-stream
}

function optimize_model() {
    local model="$1"
    local optimized_name="$2"
    
    if [ -z "$model" ] || [ -z "$optimized_name" ]; then
        echo "Usage: optimize_model [source_model] [optimized_name]"
        return 1
    fi
    
    echo "Creating optimized model $optimized_name from $model"
    docker exec -it ollama bash -c "echo 'FROM $model
PARAMETER temperature 1
PARAMETER top_k 40
PARAMETER top_p 0.9
PARAMETER num_ctx 2048
PARAMETER num_thread 4' > /tmp/$optimized_name.modelfile && ollama create $optimized_name -f /tmp/$optimized_name.modelfile"
    
    echo "Optimized model created. Test with: ./model-manager.sh benchmark $optimized_name"
}

function pull_model() {
    local model="$1"
    
    if [ -z "$model" ]; then
        echo "Please specify a model to pull (e.g. phi2, mistral, etc.)"
        return 1
    fi
    
    echo "Pulling model: $model"
    docker exec -it ollama ollama pull $model
}

# Main script logic
command=$1
case "$command" in
    list)
        list_models
        ;;
    benchmark)
        benchmark_model "$2"
        ;;
    optimize)
        optimize_model "$2" "$3"
        ;;
    pull)
        pull_model "$2"
        ;;
    help|*)
        echo "LLM Model Manager"
        echo "Usage: ./model-manager.sh [command] [options]"
        echo ""
        echo "Commands:"
        echo "  list                 List all available models"
        echo "  benchmark [model]    Test response speed of a model"
        echo "  optimize [src] [dst] Create optimized version of a model"
        echo "  pull [model]         Download a new model"
        echo "  help                 Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./model-manager.sh list"
        echo "  ./model-manager.sh benchmark fast-tinyllama"
        echo "  ./model-manager.sh optimize tinyllama fast-tiny"
        echo "  ./model-manager.sh pull phi2"
        ;;
esac
