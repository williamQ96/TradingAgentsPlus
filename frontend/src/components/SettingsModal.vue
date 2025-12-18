<script setup>
import { ref, onMounted } from 'vue';
import { X, Save, Key, ShieldCheck, Server } from 'lucide-vue-next';

const props = defineProps({
  isOpen: Boolean
});

const emit = defineEmits(['close']);

const openaiKey = ref('');
const anthropicKey = ref('');
const googleKey = ref('');
const groqKey = ref('');
const deepseekKey = ref('');
const qwenKey = ref('');
const ollamaUrl = ref('http://localhost:11434/v1');
const alphaVantageKey = ref('');

const saved = ref(false);

onMounted(() => {
  openaiKey.value = localStorage.getItem('TA_OPENAI_API_KEY') || '';
  anthropicKey.value = localStorage.getItem('TA_ANTHROPIC_API_KEY') || '';
  googleKey.value = localStorage.getItem('TA_GOOGLE_API_KEY') || '';
  groqKey.value = localStorage.getItem('TA_GROQ_API_KEY') || '';
  deepseekKey.value = localStorage.getItem('TA_DEEPSEEK_API_KEY') || '';
  qwenKey.value = localStorage.getItem('TA_QWEN_API_KEY') || '';
  ollamaUrl.value = localStorage.getItem('TA_OLLAMA_URL') || 'http://localhost:11434/v1';
  alphaVantageKey.value = localStorage.getItem('TA_ALPHA_VANTAGE_API_KEY') || '';
});

const saveSettings = () => {
  localStorage.setItem('TA_OPENAI_API_KEY', openaiKey.value);
  localStorage.setItem('TA_ANTHROPIC_API_KEY', anthropicKey.value);
  localStorage.setItem('TA_GOOGLE_API_KEY', googleKey.value);
  localStorage.setItem('TA_GROQ_API_KEY', groqKey.value);
  localStorage.setItem('TA_DEEPSEEK_API_KEY', deepseekKey.value);
  localStorage.setItem('TA_QWEN_API_KEY', qwenKey.value);
  localStorage.setItem('TA_OLLAMA_URL', ollamaUrl.value);
  localStorage.setItem('TA_ALPHA_VANTAGE_API_KEY', alphaVantageKey.value);
  
  saved.value = true;
  setTimeout(() => {
    saved.value = false;
    emit('close');
  }, 800);
};
</script>

<template>
  <Teleport to="body">
    <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm transition-opacity" @click="$emit('close')"></div>

      <!-- Modal -->
      <div class="relative w-full max-w-2xl bg-white rounded-2xl shadow-2xl ring-1 ring-black/5 flex flex-col max-h-[90vh]">
        
        <!-- Header -->
        <div class="p-6 border-b border-gray-100 flex items-center justify-between shrink-0">
            <div class="flex items-center gap-3">
                <div class="p-2 bg-emerald-50 rounded-lg text-emerald-600">
                    <Key class="w-6 h-6" />
                </div>
                <div>
                    <h3 class="text-xl font-bold text-gray-900">TradingAgent Plus Configuration</h3>
                    <p class="text-xs text-gray-500">Securely configure your AI models and data feeds.</p>
                </div>
            </div>
            <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 transition p-1 hover:bg-gray-100 rounded-full">
                <X class="w-6 h-6" />
            </button>
        </div>

        <!-- Scrollable Content -->
        <div class="flex-1 overflow-y-auto p-6 custom-scrollbar">
            <form @submit.prevent="saveSettings" class="space-y-8">
            
            <!-- Data Vendors -->
            <div>
                <h4 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4 border-b border-gray-100 pb-2">Data Venders (Required)</h4>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Alpha Vantage API Key</label>
                    <div class="relative">
                        <input v-model="alphaVantageKey" type="password" placeholder="YOUR_KEY" 
                            class="w-full pl-10 pr-3 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:bg-white outline-none transition text-sm font-mono text-gray-600 placeholder:text-gray-400" />
                        <ShieldCheck class="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                    </div>
                </div>
            </div>

            <!-- Model Providers -->
            <div>
                <h4 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4 border-b border-gray-100 pb-2">LLM Providers</h4>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <!-- OpenAI -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">OpenAI API Key</label>
                        <input v-model="openaiKey" type="password" placeholder="sk-..." class="input-field" />
                    </div>

                    <!-- Anthropic -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Anthropic (Claude) Key</label>
                        <input v-model="anthropicKey" type="password" placeholder="sk-ant-..." class="input-field" />
                    </div>

                    <!-- Google -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Google Gemini Key</label>
                        <input v-model="googleKey" type="password" placeholder="AIza..." class="input-field" />
                    </div>

                    <!-- Groq -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Groq API Key</label>
                        <input v-model="groqKey" type="password" placeholder="gsk_..." class="input-field" />
                    </div>

                    <!-- Deepseek -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Deepseek API Key</label>
                        <input v-model="deepseekKey" type="password" placeholder="sk-..." class="input-field" />
                    </div>

                    <!-- Qwen -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Qwen (DashScope) Key</label>
                        <input v-model="qwenKey" type="password" placeholder="sk-..." class="input-field" />
                    </div>
                </div>

                <!-- Local / Ollama -->
                <div class="mt-6">
                     <label class="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-2">
                        <Server class="w-4 h-4" /> Local LLM (Ollama) URL
                     </label>
                     <input v-model="ollamaUrl" type="text" placeholder="http://localhost:11434/v1" class="input-field font-mono text-gray-600" />
                </div>
            </div>

            </form>
        </div>

        <!-- Footer -->
        <div class="p-6 border-t border-gray-100 shrink-0 bg-gray-50/50 rounded-b-2xl">
            <button @click="saveSettings" class="w-full flex items-center justify-center gap-2 bg-gray-900 hover:bg-gray-800 text-white font-semibold py-3.5 rounded-xl transition-all active:scale-[0.99] shadow-lg shadow-gray-200">
               <span v-if="saved" class="flex items-center gap-2 text-emerald-400">Settings Saved!</span>
               <span v-else class="flex items-center gap-2"><Save class="w-4 h-4" /> Save Configuration</span>
            </button>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.input-field {
    @apply w-full px-3 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:bg-white outline-none transition text-sm font-mono text-gray-600 placeholder:text-gray-400;
}
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #e5e7eb;
  border-radius: 99px;
}
</style>
