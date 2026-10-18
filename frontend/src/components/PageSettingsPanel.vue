<template>
	<!-- The page's own settings, alongside the page rather than on top of it:
	     the fields here describe what is on screen, and the social preview is
	     worth watching while the meta fields change. -->
	<aside
		class="flex h-full w-[352px] shrink-0 flex-col border-l border-outline-gray-2"
		data-testid="page-settings-panel"
	>
		<div
			class="flex h-12 shrink-0 items-center justify-between gap-2 border-b border-outline-gray-2 px-3"
		>
			<span class="truncate text-base-medium text-ink-gray-8">
				{{ __('Page settings') }}
			</span>
			<Tooltip :text="__('Close page settings')">
				<Button
					variant="ghost"
					:aria-label="__('Close page settings')"
					@click="emit('close')"
				>
					<span class="lucide-x size-4" aria-hidden="true" />
				</Button>
			</Tooltip>
		</div>

		<ScrollArea class="min-h-0 flex-1" viewport-class="p-3">
			<div class="flex flex-col gap-6">
				<!-- On a git-synced page the repo owns the title, the route
				     and whether the page ships: the next sync rewrites
				     anything typed here. The social preview below is wiki-side
				     data the repo never carries, so it stays editable. -->
				<section class="flex flex-col gap-3">
					<div class="flex items-baseline justify-between gap-2">
						<h4 class="text-xs text-ink-gray-5">{{ __('General') }}</h4>
						<Badge v-if="readonly" variant="subtle" theme="gray" size="sm">
							{{ __('From the repo') }}
						</Badge>
					</div>
					<FormControl
						v-model="form.title"
						type="text"
						:label="__('Title')"
						:placeholder="__('Untitled')"
						:disabled="readonly"
					/>
					<FormControl
						v-model="form.route"
						type="text"
						:label="__('Route')"
						:placeholder="__('space/section/page')"
						:description="publicUrl"
						:disabled="readonly"
					/>
					<div class="flex items-center justify-between gap-3">
						<div class="flex flex-col">
							<span class="text-sm text-ink-gray-7">{{ __('Published') }}</span>
							<span class="text-xs text-ink-gray-5">
								{{ __('Visible on the public site') }}
							</span>
						</div>
						<Switch
							v-model="form.isPublished"
							:disabled="readonly"
							:aria-label="__('Published')"
						/>
					</div>
					<div class="flex items-center justify-between gap-3">
						<div class="flex flex-col">
							<span class="text-sm text-ink-gray-7">{{ __('Disable Indexing') }}</span>
							<span class="text-xs text-ink-gray-5">
								{{ __('Prevent search engines from indexing this page') }}
							</span>
						</div>
						<Switch
							v-model="form.disableIndexing"
							:disabled="!canEditMeta"
							:aria-label="__('Disable Indexing')"
						/>
					</div>
				</section>

				<section class="flex flex-col gap-3">
					<h4 class="text-xs text-ink-gray-5">{{ __('Social preview') }}</h4>
					<FormControl
						v-model="form.metaTitle"
						type="text"
						:label="__('Meta title')"
						:placeholder="title"
						:description="__('Leave empty to use the page title')"
						:disabled="!canEditMeta"
					/>
					<FormControl
						v-model="form.metaDescription"
						type="textarea"
						:label="__('Meta description')"
						:rows="3"
						:placeholder="__('A short summary shown in search results and link previews')"
						:description="descriptionHint"
						:disabled="!canEditMeta"
					/>
					<div class="flex flex-col gap-1.5">
						<label class="text-sm text-ink-gray-5">{{ __('Meta image') }}</label>
						<div
							v-if="form.metaImage"
							class="group relative overflow-hidden rounded-5 border border-outline-gray-2"
						>
							<img :src="form.metaImage" alt="" class="aspect-[1200/630] w-full object-cover" />
							<div
								class="absolute inset-0 flex items-center justify-center gap-2 bg-black-overlay-400 opacity-0 transition-opacity group-hover:opacity-100"
							>
								<span
									v-if="isUploadingImage"
									class="lucide-loader-2 size-5 animate-spin text-white"
									aria-hidden="true"
								/>
								<template v-else-if="canEditMeta">
									<Button size="sm" variant="solid" @click="pickImage">
										{{ __('Replace') }}
									</Button>
									<Button size="sm" variant="subtle" theme="red" @click="removeImage">
										{{ __('Remove') }}
									</Button>
								</template>
							</div>
						</div>
						<button
							v-else
							type="button"
							class="flex aspect-[1200/630] w-full flex-col items-center justify-center gap-1.5 rounded-5 border border-dashed border-outline-gray-3 bg-surface-gray-1 text-sm text-ink-gray-5 hover:bg-surface-gray-2"
							:disabled="isUploadingImage || !canEditMeta"
							@click="pickImage"
						>
							<span
								v-if="isUploadingImage"
								class="lucide-loader-2 size-5 animate-spin"
								aria-hidden="true"
							/>
							<span v-else class="lucide-image-plus size-5" aria-hidden="true" />
							<span>
								{{ isUploadingImage ? __('Uploading...') : __('Upload image') }}
							</span>
							<span class="text-xs text-ink-gray-4">
								{{ __('Recommended 1200×630') }}
							</span>
						</button>
						<input
							ref="imageInput"
							type="file"
							accept="image/*"
							class="hidden"
							@change="handleImageChange"
						/>
					</div>

					<div class="flex flex-col gap-2">
						<span class="text-sm text-ink-gray-5">{{ __('Preview') }}</span>
						<div class="flex flex-col overflow-hidden rounded-5 border border-outline-gray-2">
							<div
								class="relative flex aspect-[1200/630] w-full shrink-0 items-center justify-center bg-surface-gray-2"
							>
								<img
									v-if="previewImage"
									:src="previewImage"
									alt=""
									class="h-full w-full object-cover"
									:class="{ 'opacity-0': previewImageLoading }"
									@load="previewImageLoading = false"
									@error="previewImageFailed = true"
								/>
								<span v-else class="lucide-image size-7 text-ink-gray-3" aria-hidden="true" />
								<!-- A cold card takes a Chromium launch to render, so the
								     placeholder icon would otherwise sit there looking like
								     "no image" for seconds. -->
								<div
									v-if="previewImage && previewImageLoading"
									class="absolute inset-0 animate-pulse bg-surface-gray-3"
								/>
							</div>
							<div class="flex flex-col gap-1 border-t border-outline-gray-2 p-3">
								<span class="truncate text-xs text-ink-gray-4">{{ route }}</span>
								<span class="line-clamp-1 text-sm-medium text-ink-gray-9">
									{{ form.metaTitle || title }}
								</span>
								<span
									v-if="form.metaDescription"
									class="line-clamp-3 text-xs leading-4 text-ink-gray-6"
								>
									{{ form.metaDescription }}
								</span>
								<span v-else class="text-xs italic leading-4 text-ink-gray-3">
									{{ __('No description set') }}
								</span>
							</div>
						</div>
						<p v-if="isGeneratedPreview" class="text-xs text-ink-gray-4">
							{{ __('Auto-generated from the page metadata. Upload an image to override it.') }}
						</p>
					</div>
				</section>

				<!-- Access lives here, next to the page's other settings, instead of a
				     second toolbar dialog: the space's inherited grant is shown above
				     the page's own override, so the two systems read as one. -->
				<section class="flex flex-col gap-3 border-t border-outline-gray-2 pt-4">
					<h4 class="text-xs text-ink-gray-5">{{ __('Access') }}</h4>
					<p class="text-xs text-ink-gray-5">
						{{ __('Inherited from the space:') }}
						<span class="text-ink-gray-7">{{ inheritedAccess }}</span>
					</p>

					<template v-if="canEditAccess">
						<div class="flex flex-col gap-1.5">
							<label class="text-sm text-ink-gray-7">{{ __('This page') }}</label>
							<Select
								:model-value="accessMode"
								:options="accessModeOptions"
								:aria-label="__('This page')"
								@update:model-value="accessMode = $event"
							/>
						</div>
						<div
							v-if="accessMode === 'Restricted'"
							class="flex flex-col gap-3 rounded-8 border border-outline-gray-2 p-3"
						>
							<div class="flex flex-col gap-1.5">
								<label class="text-sm text-ink-gray-7">{{ __('Roles') }}</label>
								<MultiSelect
									v-model="accessRoles"
									:options="roleOptions"
									:placeholder="__('Choose roles')"
									:aria-label="__('Roles')"
								/>
							</div>
							<div class="flex flex-col gap-1.5">
								<label class="text-sm text-ink-gray-7">{{ __('People') }}</label>
								<MultiSelect
									v-model="accessUsers"
									:options="userOptions"
									:placeholder="__('Choose people')"
									:aria-label="__('People')"
								/>
							</div>
							<div class="flex flex-col gap-1.5">
								<label class="text-sm text-ink-gray-7">{{ __('Level') }}</label>
								<Select
									v-model="accessLevel"
									:options="accessLevelOptions"
									:aria-label="__('Level')"
								/>
							</div>
							<p class="text-xs text-ink-gray-4">
								{{ __('Child pages inherit this list. Wiki managers always keep access.') }}
							</p>
						</div>
						<Button
							variant="subtle"
							class="self-start"
							:loading="savingAccess"
							:disabled="accessMode === 'Restricted' && !accessRoles.length && !accessUsers.length"
							@click="saveAccess"
						>
							{{ __('Save access') }}
						</Button>
					</template>
					<p v-else class="text-xs text-ink-gray-4">
						{{ __('Only wiki managers can change who can read this page.') }}
					</p>
				</section>

				<section class="flex flex-col gap-2">
					<h4 class="text-xs text-ink-gray-5">{{ __('Details') }}</h4>
					<dl class="flex flex-col gap-2 text-sm">
						<div class="flex justify-between gap-3">
							<dt class="text-ink-gray-6">{{ __('Words') }}</dt>
							<dd class="text-ink-gray-8">{{ words }}</dd>
						</div>
						<div class="flex justify-between gap-3">
							<dt class="text-ink-gray-6">{{ __('Reading time') }}</dt>
							<dd class="text-ink-gray-8">
								{{ __('{0} min', [readingTime]) }}
							</dd>
						</div>
						<div v-if="lastEdited" class="flex justify-between gap-3">
							<dt class="text-ink-gray-6">{{ __('Last edited') }}</dt>
							<dd class="text-ink-gray-8">{{ lastEdited }}</dd>
						</div>
						<div v-if="lastEditedBy" class="flex min-w-0 justify-between gap-3">
							<dt class="shrink-0 text-ink-gray-6">{{ __('Edited by') }}</dt>
							<dd class="truncate text-ink-gray-8">{{ lastEditedBy }}</dd>
						</div>
					</dl>
					<!-- The raw document, for the people who can read it. It used to
					     sit in the header's action menu, beside Rename and Delete,
					     which put an admin's escape hatch on the same footing as the
					     two things everyone does to a page. -->
					<a
						v-if="deskUrl"
						:href="deskUrl"
						target="_blank"
						rel="noopener noreferrer"
						class="flex items-center gap-1.5 text-sm text-ink-gray-5 hover:text-ink-gray-7"
					>
						<span class="lucide-external-link size-3.5" aria-hidden="true" />
						{{ __('View in Desk') }}
					</a>
				</section>
			</div>
		</ScrollArea>

		<div class="shrink-0 border-t border-outline-gray-2 p-3">
			<Button
				class="w-full"
				variant="solid"
				:disabled="!isDirty || isSaving"
				:loading="isSaving"
				@click="save"
			>
				{{ __('Save') }}
			</Button>
		</div>
	</aside>
</template>

<script setup>
import { countWords, readingMinutes } from '@/lib/readingStats';
import { useDraftWorkspaceStore } from '@/stores/draftWorkspace';
import { useSpaceStore } from '@/stores/space';
import { useUserStore } from '@/stores/user';
import {
	Badge,
	Button,
	FormControl,
	MultiSelect,
	ScrollArea,
	Select,
	Switch,
	Tooltip,
	createListResource,
	createResource,
	dayjsLocal,
	toast,
	useFileUpload,
} from 'frappe-ui';
import { computed, reactive, ref, watch } from 'vue';

const props = defineProps({
	// The document resource WikiDocumentPanel already loaded. Meta fields are
	// written straight to the document (they carry no reader-visible content,
	// so they don't travel through a change request); the rest of the fields
	// go through the draft workspace.
	docResource: {
		type: Object,
		required: true,
	},
	docKey: {
		type: String,
		default: null,
	},
	// A git-synced page: the repo owns everything the change request would
	// carry, so only the meta fields are the wiki's to write.
	readonly: {
		type: Boolean,
		default: false,
	},
	// The effective values for the open page: the draft's, where it has one.
	title: {
		type: String,
		default: '',
	},
	route: {
		type: String,
		default: '',
	},
	published: {
		type: Boolean,
		default: false,
	},
	// The editor's buffer, so the counts track what is on screen.
	content: {
		type: String,
		default: '',
	},
});

const emit = defineEmits(['close', 'node-updated']);

const draftStore = useDraftWorkspaceStore();
const userStore = useUserStore();
const spaceStore = useSpaceStore();
const fileUploader = useFileUpload();

const isSaving = ref(false);
const isUploadingImage = ref(false);
const imageInput = ref(null);

// --- Access (the page's own overlay on the space's inherited grant) --------
const ACCESS_LEVEL_RANK = { Read: 1, Write: 2, Admin: 3 };
const accessMode = ref('Inherit');
const accessLevel = ref('Read');
const accessRoles = ref([]);
const accessUsers = ref([]);
const canEditAccess = ref(false);
const savingAccess = ref(false);

const accessModeOptions = computed(() => [
	{ label: __('Inherit the space'), value: 'Inherit' },
	{ label: __('Only the people and roles below'), value: 'Restricted' },
]);
const accessLevelOptions = computed(() => [
	{ label: __('Read only'), value: 'Read' },
	{ label: __('Read and edit'), value: 'Write' },
	{ label: __('Read, edit and manage access'), value: 'Admin' },
]);

const pageName = computed(() => props.docResource?.doc?.name || null);

// What the page would inherit: the space's visibility and its role grants, so
// "Inherit" is not an empty promise in the panel.
const inheritedAccess = computed(() => {
	const space = spaceStore.doc;
	if (!space) return __('the space settings');
	const visibility = space.visibility || 'Logged in';
	const roles = (space.roles || []).map(
		(role) => `${role.role} (${role.permission_level})`,
	);
	return roles.length ? `${visibility} · ${roles.join(', ')}` : visibility;
});

const accessState = createResource({
	url: 'wiki.api.access.get_page_access',
	makeParams: () => ({ docname: pageName.value }),
});
const accessSave = createResource({
	url: 'wiki.api.access.update_page_access',
	onSuccess: (data) => applyAccess(data),
	onError: (err) =>
		toast.error(err?.messages?.[0] || __('Could not save access.')),
});
const rolesList = createListResource({
	doctype: 'Role',
	fields: ['name'],
	pageLength: 999,
	auto: false,
});
const usersList = createListResource({
	doctype: 'User',
	fields: ['name', 'full_name'],
	filters: { enabled: 1 },
	pageLength: 999,
	auto: false,
});
const roleOptions = computed(() =>
	(rolesList.data || []).map((role) => ({ label: role.name, value: role.name })),
);
const userOptions = computed(() =>
	(usersList.data || [])
		.filter((user) => user.name !== 'Administrator' && user.name !== 'Guest')
		.map((user) => ({ label: user.full_name || user.name, value: user.name })),
);

function applyAccess(data) {
	accessMode.value = data?.mode || 'Inherit';
	canEditAccess.value = Boolean(data?.can_edit);
	accessRoles.value = [];
	accessUsers.value = [];
	let strongest = 'Read';
	for (const entry of data?.entries || []) {
		if (entry.subject_type === 'Role') accessRoles.value.push(entry.role);
		else accessUsers.value.push(entry.user);
		if ((ACCESS_LEVEL_RANK[entry.level] || 0) > (ACCESS_LEVEL_RANK[strongest] || 0)) {
			strongest = entry.level;
		}
	}
	accessLevel.value = strongest;
}

async function loadAccess() {
	if (!pageName.value) return;
	try {
		applyAccess(await accessState.fetch());
		if (canEditAccess.value) {
			rolesList.fetch();
			usersList.fetch();
		}
	} catch {
		// A page the reader cannot manage simply keeps the inherited line.
	}
}

async function saveAccess() {
	savingAccess.value = true;
	const entries = [
		...accessRoles.value.map((role) => ({
			subject_type: 'Role',
			role,
			level: accessLevel.value,
		})),
		...accessUsers.value.map((user) => ({
			subject_type: 'User',
			user,
			level: accessLevel.value,
		})),
	];
	try {
		applyAccess(
			await accessSave.submit({
				docname: pageName.value,
				mode: accessMode.value,
				entries,
			}),
		);
		toast.success(__('Access saved'));
	} finally {
		savingAccess.value = false;
	}
}

watch(pageName, loadAccess, { immediate: true });

const form = reactive({
	title: '',
	route: '',
	isPublished: false,
	metaTitle: '',
	metaDescription: '',
	metaImage: '',
	disableIndexing: false,
});

// The saved values every field is measured against — the panel is a form, not
// a set of live controls, so nothing lands until Save.
const saved = computed(() => ({
	title: props.title || '',
	route: props.route || '',
	isPublished: Boolean(props.published),
	metaTitle: props.docResource.doc?.meta_title || '',
	metaDescription: props.docResource.doc?.meta_description || '',
	metaImage: props.docResource.doc?.meta_image || '',
	disableIndexing: Boolean(props.docResource.doc?.disable_indexing),
}));

// The title is also edited in the prose column, and the tree renames pages
// behind the panel's back. Adopt an outside change only for a field the user
// has not touched: a field that already diverges from the old saved value is
// theirs until they save or the page changes.
watch(
	saved,
	(next, previous) => {
		for (const [field, value] of Object.entries(next)) {
			if (!previous || form[field] === previous[field]) form[field] = value;
		}
	},
	{ immediate: true },
);

const META_FIELDS = [
	'metaTitle',
	'metaDescription',
	'metaImage',
	'disableIndexing',
];

// Meta fields are written to the document, which takes space write access.
// Contributing through a change request is not enough.
const canEditMeta = computed(() => spaceStore.canWriteSpace);

const isDirty = computed(() =>
	Object.entries(saved.value).some(
		([field, value]) =>
			(!props.readonly || META_FIELDS.includes(field)) && form[field] !== value,
	),
);

const publicUrl = computed(() =>
	form.route ? `${window.location.origin}/${form.route}` : '',
);

const descriptionHint = computed(() =>
	__('Recommended: 150-160 characters ({0} so far)', [
		form.metaDescription.length,
	]),
);

const words = computed(() => countWords(props.content));
const readingTime = computed(() => readingMinutes(words.value));

const lastEdited = computed(() => {
	const modified = props.docResource.doc?.modified;
	return modified ? dayjsLocal(modified).fromNow() : '';
});
// Only a Wiki Manager can open the Desk form, so only they are offered it.
const deskUrl = computed(() => {
	const name = props.docResource.doc?.name;
	if (!name || !userStore.isWikiManager) return '';
	return `/app/wiki-document/${encodeURIComponent(name)}`;
});

const lastEditedBy = computed(() => props.docResource.doc?.modified_by || '');

// With no uploaded image the page still ships an og:image — the generated card
// from wiki/api/og_image.py. Preview the real endpoint rather than a mock, so
// what this box shows is literally what a scraper will fetch. The endpoint 404s
// for every case that emits no card (setting off, unpublished, group, external
// link, no space, render failure), which is what the @error fallback catches.
// `v` is ignored server-side and exists only to force a refetch after a save
// that changed the card's inputs — bumping per save rather than per keystroke
// keeps it to one extra render instead of one per character typed.
const previewVersion = ref(0);
const previewImageFailed = ref(false);
const previewImageLoading = ref(true);

const generatedPreview = computed(() => {
	const route = props.docResource.doc?.route;
	if (!route) return '';
	return `/api/method/wiki.api.og_image.og_image?route=${encodeURIComponent(
		route,
	)}&v=${previewVersion.value}`;
});

const previewImage = computed(() => {
	if (form.metaImage) return form.metaImage;
	return previewImageFailed.value ? '' : generatedPreview.value;
});

// Every new URL is a fresh load, so the skeleton comes back until it decodes.
watch(previewImage, (url) => {
	previewImageLoading.value = Boolean(url);
});

const isGeneratedPreview = computed(
	() => !form.metaImage && Boolean(previewImage.value),
);

// A page switch discards whatever was typed: the fields describe a page, and
// carrying them across would rename the one you just opened. Declared after
// the `saved` watcher so it wins the same flush.
watch(
	() => props.docKey,
	() => {
		Object.assign(form, saved.value);
		previewImageFailed.value = false;
		previewImageLoading.value = true;
	},
);

function pickImage() {
	imageInput.value?.click();
}

function removeImage() {
	form.metaImage = '';
}

async function handleImageChange(event) {
	const file = event.target.files?.[0];
	// Reset the input so re-selecting the same file still fires `change`.
	event.target.value = '';
	if (!file) return;

	isUploadingImage.value = true;
	try {
		const result = await fileUploader.upload(file, {
			private: false,
			// Hit our handler directly (not via upload_file's `method`
			// delegation, which would recurse). It converts PNG/JPEG to WebP
			// when the Wiki Setting is enabled, returning the optimized
			// file_url.
			upload_endpoint: '/api/method/wiki.api.upload_wiki_asset',
		});
		form.metaImage = result.file_url;
	} catch (error) {
		toast.error(error.messages?.[0] || __('Failed to upload image'));
	} finally {
		isUploadingImage.value = false;
	}
}

// The identifying fields are only ever changed, never cleared: an empty title
// or route would leave the page unreachable, and the backend would take it.
function nodeChanges() {
	const changes = {};
	// The repo is the source for all of these; a change request cannot carry
	// them, and the panel's inputs are disabled anyway.
	if (props.readonly) return changes;
	const current = saved.value;
	if (form.title.trim() && form.title !== current.title) {
		changes.title = form.title.trim();
	}
	const route = form.route.trim().replace(/^\/+/, '');
	if (route && route !== current.route) changes.route = route;
	if (form.isPublished !== current.isPublished) {
		changes.is_published = form.isPublished ? 1 : 0;
	}
	return changes;
}

function metaChanges() {
	const changes = {};
	const current = saved.value;
	if (form.metaTitle !== current.metaTitle) changes.meta_title = form.metaTitle;
	if (form.metaDescription !== current.metaDescription) {
		changes.meta_description = form.metaDescription;
	}
	if (form.metaImage !== current.metaImage) changes.meta_image = form.metaImage;
	if (form.disableIndexing !== current.disableIndexing) {
		changes.disable_indexing = form.disableIndexing ? 1 : 0;
	}
	return changes;
}

async function save() {
	const node = nodeChanges();
	const meta = metaChanges();
	isSaving.value = true;
	try {
		if (Object.keys(node).length) {
			if (!props.docKey) throw new Error(__('No active change request'));
			await draftStore.updateNode(props.docKey, node);
			emit('node-updated');
		}
		if (Object.keys(meta).length) {
			await props.docResource.updateMeta.submit(meta);
		}
		toast.success(__('Page settings saved'));
		// Retry a preview that failed before this save fixed its inputs.
		previewImageFailed.value = false;
		previewVersion.value += 1;
	} catch (error) {
		toast.error(
			error.messages?.[0] || error.message || __('Error saving page settings'),
		);
	} finally {
		isSaving.value = false;
	}
}
</script>
