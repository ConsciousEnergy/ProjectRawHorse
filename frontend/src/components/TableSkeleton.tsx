import SkeletonLoader from './SkeletonLoader';

/** Reusable skeleton loader for table pages (Browse, FOIA Targets, etc.) */
export function TableSkeleton() {
  return <SkeletonLoader type="table" />;
}

export default TableSkeleton;
