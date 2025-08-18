/**
 * WordPress dependencies
 */
import {
	switchUserToAdmin,
	visitAdminPage,
	switchUserToTest,
	isCurrentURL,
} from '@wordpress/e2e-test-utils';

/**
 * Deactivates all Site Kit utility plugins.
 */
export async function deactivateUtilityPlugins() {
	await switchUserToAdmin();

	if ( ! isCurrentURL( 'wp-admin/plugins.php' ) ) {
		await visitAdminPage( 'plugins.php' );
	}

	await page.waitForSelector( '#wpfooter' );

	const activeUtilities = await page.$$eval(
		'.active[data-plugin^="google-site-kit-test-plugins/"]',
		( rows ) => {
			return rows.map( ( row ) => row.dataset.plugin );
		}
	);

	// Bail if there are no plugins to deactivate
	if ( ! activeUtilities.length ) {
		return;
	}

	// Check the boxes of plugins to deactivate.
	await page.$$eval(
		'.active[data-plugin^="google-site-kit-test-plugins/"] input[type="checkbox"]',
		( checkboxes ) => {
			checkboxes.forEach( ( checkbox ) => ( checkbox.checked = true ) );
		}
	);

	// Bulk deactivate (robust: choose available toolbar and wait for navigation first).
	const bottomSelect = 'select#bulk-action-selector-bottom';
	const topSelect = 'select#bulk-action-selector-top';
	const bottomApply = '#doaction2';
	const topApply = '#doaction';

	// Prefer bottom controls if present; fall back to top.
	let selectSelector = topSelect;
	let applySelector = topApply;

	if ( await page.$( bottomSelect ) ) {
		selectSelector = bottomSelect;
		if ( await page.$( bottomApply ) ) {
			applySelector = bottomApply;
		}
	}

	// eslint-disable-next-line no-console
	console.debug(
		`UTIL: deactivateUtilityPlugins -> using controls select="${ selectSelector }", apply="${ applySelector }"`
	);

	await page.select( selectSelector, 'deactivate-selected' );

	await Promise.all( [
		page.waitForNavigation( {
			waitUntil: 'domcontentloaded',
			timeout: 15000,
		} ),
		page.click( applySelector ),
	] );
	await switchUserToTest();
}
