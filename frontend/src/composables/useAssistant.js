import { ref } from 'vue';

/**
 * One assistant entry point for the whole app: the command palette opens it and
 * the dialog reads the same ref. There is no second floating button — asking is
 * a command inside ⌘K, next to search.
 */
const open = ref(false);
const initialQuestion = ref('');

export function useAssistant() {
	function ask(question = '') {
		initialQuestion.value = String(question || '');
		open.value = true;
	}
	function close() {
		open.value = false;
	}
	return { open, initialQuestion, ask, close };
}
